## Scraping ZUS Coffee's Google reviews 

## Purpose
The purpose of this project is to:
1. Gain knowledge on how to scrape Google reviews.
2. Manipulate elements such as clicking on buttons, scrolling into views, waiting for elements to fully load etc.

## Output
1. Script is able to extract all reviews from each store based on the "store_data.json" which contains the addresses (google map hyperlink) scraped from ZUS Coffee's offical website.
2. Further insights can be generated such as average store rating by state, rating increase/decrease trend over time etc.

# Limitation
1. Code is not equipped to bypass bot-detection (if any)
2. Code uses class name to target elements which may not be robust to webpage changes.
3. No multiprocessing, at least more than 1 hour needed to parse through > 500 stores. 

# Disclaimer
This project is for educational purposes, I have no affiliation with the site and neither I nor the software would be held liable for any consequences resulting from its use.
Extracted data is not to be used for commercial purpose.
