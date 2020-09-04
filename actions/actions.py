#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#high level actions, that doesn't belong to page objects or helpers
from helpers.driver_helper import DriverHelper
from pages.search_page import SearchPage
from pages.listing_page import ListingPage
from helpers.mongo_helper import MongoHelper
import datetime
import traceback


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
    number_of_failed_tries_to_scrape_listing = 0
    error_per_serch_page_threshold = 2 # total number of listings on the search page is 200
    
    for link_and_date in advert_links_and_dates:
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
            continue
        
        listing.creation_date = date
        listing.search_term = search_term
        driver_helper.close_current_tab_and_go_to_the_first_one()
        if mongo_helper.get_listing_by_id(listing._id):
            there_are_new_listings = False
            break
        mongo_helper.insert_listing(listing)
    return there_are_new_listings

def check_active_listings(search_term):
    mongo_helper = MongoHelper()
    mongo_helper.start_client_and_connect()
    active_listings = mongo_helper.get_active_listings(search_term)
    #print("There are {0} active listings in db".format(len(active_listings)))
    driver_helper = DriverHelper()
    driver_helper.start_driver()
    for listing in active_listings:
        update_active_listing(listing)
    driver_helper.quit_driver()
    mongo_helper.close_connection()

def update_active_listing(listing):
    print("Checking listing {0}".format(listing["link"]))
    driver_helper = DriverHelper()
    mongo_helper = MongoHelper()
    listing_page = ListingPage.open_url(listing["link"])
    if not listing_page.is_active():
        print("The listing {0} page is not active".format(listing["link"]))
        closure_reason = listing_page.get_closure_reason()
        closure_date =  listing_page.closure_date()
        final_price = listing_page.get_price()
        fianl_shipping_cost = listing_page.get_shipping_cost()
        mongo_helper.update_listing(listing._id, "final_price", final_price)
        mongo_helper.update_listing(listing._id, "fianl_shipping_cost", fianl_shipping_cost)
        mongo_helper.update_listing(listing._id, "closure_reason", closure_reason)
        mongo_helper.update_listing(listing._id, "active", False)
        # also would be nice to check if all other parameters of the advert changed and save time of the last check,
        # but it's for the next itteration
        