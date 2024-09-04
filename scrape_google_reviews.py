# from selenium.webdriver import Chrome
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.keys import Keys

# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

import json
import time
from datetime import datetime
from lxml import html
from tqdm import tqdm
import pandas as pd

# store_data_json = 'store_data copy.json'
store_data_json = 'store_data.json'

def get_driver():
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument(f"--user-agent={user_agent}")
    
    # service = Service(executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    driver = webdriver.Chrome(options=chrome_options)
    # driver = Chrome(service=Service(ChromeDriverManager().install()),
                                    # options=chrome_options)
    
    return driver

def read_json(f):
    with open(f, 'r') as json_file:
        json_obj = json.load(json_file)
    
    return json_obj

def get_store_metadata(driver, url):
    driver.get(url)
    driver.maximize_window()

    for i in range(3):
        time.sleep(i)
        # print(f"sleeping on {i}")
    
    store_metadata = {}
    
    # get store title,  address, ratings, review_count
    # get store title
 
    try:
        xpath_query= "//div[@class='TIHn2 ']/div[@class='tAiQdd']//h1[@class='DUwDvf lfPIob']"
        name = driver.find_element("xpath", xpath_query)
        print(name.text)

        store_metadata['name'] = name.text
        
    except NoSuchElementException:
        store_metadata['name'] = None

    # wont be able to find if no ratings
    # rating
    try:
        xpath_query = "//div[@class='TIHn2 ']/div[@class='tAiQdd']//div[@class='F7nice ']/span/span[@aria-hidden='true']"
        store_rating = driver.find_element("xpath", xpath_query)
        store_metadata['store_rating'] = store_rating.get_attribute("innerHTML")

    # review count
        xpath_query = "//div[@class='TIHn2 ']/div[@class='tAiQdd']//div[@class='F7nice ']//span[contains(@aria-label,'reviews')]"
        review_count_ele = driver.find_element("xpath", xpath_query)
        review_count = review_count_ele.get_attribute("innerHTML")[1:-1]
        review_count = int(review_count.replace(",", ""))
        store_metadata["store_review_count"] = review_count
        
    except NoSuchElementException:
        store_metadata['store_rating'] = None
        store_metadata["store_review_count"] = 0

    # address
    try:
        xpath_query = "//button[@data-item-id='address']//div[@class='Io6YTe fontBodyMedium kR99db fdkmkc ']"
        address = driver.find_element("xpath", xpath_query)
        store_metadata["address"] = address.get_attribute("innerHTML")
    
    except NoSuchElementException:
        store_metadata['address'] = None
    
    
    return store_metadata, driver
    
def get_store_reviews(driver, store_review_count):
    
    # click button with attribute aria-label has the word "Reviews"
    xpath_query = "//button[contains(@aria-label, 'Reviews')]"
    buttons = driver.find_elements("xpath", xpath_query)
    buttons[0].click()
        

    # Define the XPath of the element to be scrolled into view
    target_xpath = "//div[@class='lXJj5c Hk4XGb ']/div[@class='qjESne ']"

    # keep scrolling until reached the end (count of unique review ID = review count)
    while True:
        try:
            element = driver.find_element(By.XPATH, target_xpath)
            driver.execute_script("arguments[0].scrollIntoView();", element)
        
            review_id_xpath = "//div[@class='jftiEf fontBodyMedium ' and @data-review-id]"
            # review_id_xpath = "//div[@class='m6QErb XiKgde']/div[@class='jftiEf fontBodyMedium ' and @data-review-id]"
            review_id_elements = driver.find_elements(By.XPATH, review_id_xpath)
            review_id_count = len(review_id_elements)
        
            if review_id_count == store_review_count:
                break
                       
        except (NoSuchElementException, StaleElementReferenceException):  
            break
        
    for i in range(3):
        time.sleep(i)


    # click the "More" button on each reviews
    see_more_button_xpath = "//span/button[@class='w8nwRe kyuRq']"
    see_more_buttons = driver.find_elements(By.XPATH, see_more_button_xpath)
    
    if see_more_buttons:
        for button in see_more_buttons:
            button.click()
            

    # Find the element containing all reviews
    # reviews_container_xpath = "//div[@class='m6QErb ']"
    reviews_container_xpath = "//div[@class='w6VYqd']"
    reviews_container = driver.find_element(By.XPATH, reviews_container_xpath)

    # Get the HTML content of the reviews container
    reviews_html = reviews_container.get_attribute("outerHTML")

    # Parse the reviews HTML content
    parsed_reviews_html = html.fromstring(reviews_html)

    # Use XPath to search for review elements
    reviews_elements = parsed_reviews_html.xpath("//div[@class='jftiEf fontBodyMedium ']")
    # reviews_elements = parsed_reviews_html.xpath("//div[@class='m6QErb ']/div[@class='jftiEf fontBodyMedium ']")

    extracted_reviews = []
    for review_element in reviews_elements:
        review_dic = {}
        
        # Extract reviewer name and review ID
        reviewer_name = review_element.get("aria-label")
        review_id = review_element.get("data-review-id")

        # Extract review stars and timeline
        span_elements = review_element.xpath(".//div[@class='GHT2ce']/div[@class='DU9Pgb']/span")
        review_stars = span_elements[0].get("aria-label")
        review_timeline = span_elements[1].text_content()

        # Extract review text (if available)
        review_text_element = review_element.xpath(f".//div[@id='{review_id}']/span[@class='wiI7pd']")
        review_text = review_text_element[0].text_content() if review_text_element else None

        # Extract review response (if available)
        review_response_element = review_element.xpath(f".//div[@data-review-id='{review_id}']//div[@class='CDe7pd']/div[@class='wiI7pd']")
        review_response = review_response_element[0].text_content() if review_response_element else None

        # Store review data in a dictionary
        review_dic["review_id"] = review_id
        review_dic["reviewer_name"] = reviewer_name
        review_dic["review_stars"] = review_stars
        review_dic["review_timeline"] = review_timeline
        review_dic["review_text"] = review_text
        review_dic["review_response"] = review_response
        
        # Append the review dictionary to the list of extracted reviews
        extracted_reviews.append(review_dic)

    # a list of review dictionaries = extracted_reviews
    return extracted_reviews

def get_time():
    now_time = datetime.now()
    now_time = now_time.strftime("%Y%m%d%H%M%S")
    return now_time


def write_to_json(full_dict):
    # script_endtime = get_time()
    with open(f"store_data_w_reviews_{script_runtime}.json", "w") as json_file:
        json.dump(full_dict, json_file, indent=4)

def validate_store_details(json_obj):
    total_store = 0
    total_review_mismatches_stores = 0 
    
    all_mismatches = []
    all_store_count = []
    
    for state, store_details in json_obj["state"].items():
        # print(f"State: {state}")
        
        store_count = {}
        num_stores = len(store_details)
        total_store += num_stores
        
        store_count["state"] = state
        store_count["store_count"] = num_stores
        store_count["cumulative"] = total_store
        
        all_store_count.append(store_count)
        
        print(f"State: {state}, Number of Stores: {num_stores}")
        # Iterate through each store in the state
        for store in store_details:
            mismatch_reviews_stores = {}
            
            if store["store_name"] == "" or store["store_address"] == "":
                print(f"{store} Empty values detected!")
                
            store_review_count = int(store["store_review_count"])
            actual_store_review_count = len(store["reviews"])            
            
            if store_review_count != actual_store_review_count:
                # print(f"{store['store_name']} has mismatch reviews")
                total_review_mismatches_stores += 1
                
                mismatch_reviews_stores["store"] = store["store_name"]
                mismatch_reviews_stores["actual_store_review_count"] = actual_store_review_count
                mismatch_reviews_stores["store_review_count"] = store_review_count
                mismatch_reviews_stores["store_link"] = store["store_link"]
                all_mismatches.append(mismatch_reviews_stores)
                
                # print(mismatch_reviews_stores)

    df = pd.DataFrame(all_mismatches)
    df.to_csv(f"mismatches_{script_runtime}.csv", index=None)
    
    df = pd.DataFrame(all_store_count)
    df.to_csv(f"all_store_count_{script_runtime}.csv", index=None)

    print(f"Total store count: {total_store}")
    print(f"Total store review mismatch count: {total_review_mismatches_stores}")
    

def main():
    try:
        store_json = read_json(store_data_json)
        
        current_state_count = 1
        total_states = len(store_json["state"].items())
        # loop through each state, for each store, pass the url to the function
        for k1, v1 in store_json["state"].items():
        
            for store in tqdm(v1, desc=f"Store: {k1}. State: {current_state_count}/{total_states}"):
                store_link = store["store_link"]
                
                driver = get_driver()
                
                # process each url
                # extracted_reviews_list, store_metadata = process_google_map(driver, store_link)
                
                store_metadata, driver = get_store_metadata(driver,store_link)
                
                store_review_count = store_metadata["store_review_count"]
                
                if store_review_count > 0:
                    extracted_reviews_list = get_store_reviews(driver, store_review_count)
                else:
                    extracted_reviews_list = []
                
                store["reviews"] = extracted_reviews_list
                store.update(store_metadata)

                driver.close()
                
            current_state_count += 1
                
        write_to_json(store_json)
        validate_store_details(store_json)
    except KeyboardInterrupt:
        write_to_json(store_json)
if __name__ == "__main__":
    
    script_runtime = get_time()
    
    
    main()










    
    









        
