#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#high level actions, that doesn't belong to page objects or helpers
from helpers.driver_helper import DriverHelper
from pages.search_page import SearchPage
from pages.listing_page import ListingPage
from helpers.mongo_helper import MongoHelper
import datetime
import traceback
import time


def scrape_new_listings(search_term):
    # open initial search page for search_term with predefined search criterias. See search criterias in SearchPage
    driver_helper = DriverHelper()
    driver_helper.start_driver()
    mongo_helper = MongoHelper()
    mongo_helper.start_client_and_connect()
    print("Searching new listings for '{0}' keyword".format(search_term))
    search_page = SearchPage.open_it_via_url(search_term)
    there_are_new_listings = True
    there_are_more_pages = True
    while (there_are_new_listings & there_are_more_pages):
        there_are_new_listings = scrape_search_results_from_the_currenst_search_page(search_term)
        there_are_more_pages = search_page.go_to_the_next_page_if_available()
        print("There are new pages available: {0}\nThere are new listings: {1}".format(there_are_more_pages, there_are_new_listings))
    driver_helper.quit_driver()
    mongo_helper.close_connection()
        
def scrape_search_results_from_the_currenst_search_page(search_term):
    search_page = SearchPage()
    driver_helper = DriverHelper()
    mongo_helper = MongoHelper()
    
    advert_links_and_dates = search_page.get_listing_links_and_dates()
    there_are_new_listings = True if len(advert_links_and_dates) > 0 else False
    
    # Could be that scraping of the listing page will fail because of some edge cases and network issues
    # I'd like to have info about the fils in the logs, but still continue scraping if the amount of failures is small
    # TODO: replace threshold with retry after testing
    number_of_failed_tries_to_scrape_listing = 0
    error_per_serch_page_threshold = 2 # total number of listings on the search page is 50
    
    # Sometimes after navigation to the next page we see the last listing form the previos page on it
    # Adding threshold to avoid false conclusion that there are only already saved listings on the page
    number_of_existing_listings_on_the_page = 0
    existing_listings_on_the_page_threshold = 3
    
    for link_and_date in advert_links_and_dates:
        print("Listing date: {}".format(link_and_date["date"]))
        #next line was used for initial run
        #if (("Mai" in link_and_date["date"]) or ("Apr" in link_and_date["date"])):
            #return False
        link = link_and_date["link"]
        date = "{0} {1}".format(link_and_date["date"], datetime.datetime.now().year)
        try:
            print("Scraping listing {0}".format(link))
            listing_page = ListingPage.open_url_in_the_new_tab(link)
            listing = listing_page.get_listing_data()
        except Exception as e:
            trace = traceback.format_exc()
            print("Failed to scrape the listing")
            print(e)
            print(trace)
            number_of_failed_tries_to_scrape_listing += 1
            if (number_of_failed_tries_to_scrape_listing > error_per_serch_page_threshold):
                raise Exception("More than {0} scraping failures for the search result page".format(error_per_serch_page_threshold))
            driver_helper.close_current_tab_and_go_to_the_first_one()
            continue
        
        listing.creation_date = date
        listing.search_term = search_term
        driver_helper.close_current_tab_and_go_to_the_first_one()
        if ((len(mongo_helper.get_listing_by_id(listing._id)) > 0) & (number_of_existing_listings_on_the_page > existing_listings_on_the_page_threshold)):
            print("This listing is already in the db")
            print("Number of the listings that were already saved in the db on the current search page is {0}".format(number_of_existing_listings_on_the_page))
            there_are_new_listings = False
            break
        elif (mongo_helper.get_listing_by_id(listing._id)):
            print("This listing is already in the db: {0}".format(link))
            if (mongo_helper.get_listing_by_id(listing._id)[0]["search_term"] == search_term):
                number_of_existing_listings_on_the_page += 1
            else:
                print("This listing was saved in database for the different search term")
            continue
        mongo_helper.insert_listing(listing)
       
    return there_are_new_listings

def check_active_listings(search_term):
    mongo_helper = MongoHelper()
    mongo_helper.start_client_and_connect()
    active_listings = mongo_helper.get_active_listings(search_term)
    print("There are {0} active listings in db".format(active_listings.count()))
    driver_helper = DriverHelper()
    driver_helper.start_driver()
    #TODO: replace threshold with retry after testing
    number_of_failed_tries_to_scrape_listing = 0
    error_per_serch_page_threshold = 20
    for listing in active_listings.batch_size(10):
        try:
            update_active_listing(listing)
        except Exception as e:
            trace = traceback.format_exc()
            print("Failed to scrape the listing")
            print(e)
            print(trace)
            number_of_failed_tries_to_scrape_listing += 1
            if (number_of_failed_tries_to_scrape_listing > error_per_serch_page_threshold):
                raise Exception("More than {0} scraping failures for the search term {1}".format(error_per_serch_page_threshold, search_term))
            continue
    driver_helper.quit_driver()
    mongo_helper.close_connection()

def update_active_listing(listing):
    print("Checking listing {0}".format(listing["link"]))
    driver_helper = DriverHelper()
    mongo_helper = MongoHelper()
    listing_page = ListingPage.open_url(listing["link"])
    if not listing_page.is_active():
        print("The listing {0} page is NOT ACTIVE".format(listing["link"]))
        closure_date = None
        try:
            closure_date =  listing_page.get_closure_date()
        except:
            # it's fine if the product is just out of stock
            print("there is no closure data for this closed listing. Checking if it's just out of stock")
            print(listing_page.get_closure_reason())
            assert listing_page.get_closure_reason() == 'Dieser Artikel ist nicht vorrätig.'
        listing_page.open_original_listing_if_the_link_is_available()
        closure_reason = listing_page.get_closure_reason()
        final_price = listing_page.get_price()
        fianl_shipping_cost = listing_page.get_shipping_cost()
        mongo_helper.update_listing(listing["_id"], "last_update", datetime.datetime.now().strftime('%d. %b. %Y'))
        mongo_helper.update_listing(listing["_id"], "final_price", final_price)
        mongo_helper.update_listing(listing["_id"], "fianl_shipping_cost", fianl_shipping_cost)
        mongo_helper.update_listing(listing["_id"], "closure_reason", closure_reason)
        mongo_helper.update_listing(listing["_id"], "closure_date", closure_date)
        mongo_helper.update_listing(listing["_id"], "active", False)
        # also would be nice to check if all other parameters of the advert changed and save time of the last check,
        # but it's for the next itteration
    else:
        print("The listing {0} page is ACTIVE".format(listing["link"]))
        