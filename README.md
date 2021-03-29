# This repo curretnly contains several parts of the https://www.mein-iphone-verkaufen.de/ project
# TODO: clean all the parts and move them to the separate repository!

# PARTS:

# Scraping data
The aim of this project is collecting data about used iphones sales from ebay.de. 
All data is stored in the mongo database.

## scrape_new_pages.py
script scrapes new listings

## check_existing_listings.py
checks all the active listings from the database, in case some listing is not active any more, it marks this listing as inactive and adds data about closure reason, final price, final shipping cost, date of sale

# Data analysis and regression model

## explore_data_only.ipynb - exploring data without making actions on it

## prepare_data_reg.ipynb - preaparing data for the regression model

## regression.ipynb - regression model 

# Backend app

## app.py
