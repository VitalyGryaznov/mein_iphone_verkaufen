# scrape_sales_data

The aim of this project is collecting data about used iphones sales from ebay.de. 
All data is stored in the mongo database.

## scrape_new_pages.py
script scrapes new listings

## check_existing_listings.py
checks all the active listings from the database, in case some listing is not active any more, it marks this listing as inactive and adds data about closure reason, final price, final shipping cost, date of sale
