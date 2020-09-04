#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  2 07:05:22 2019

@author: vitaly.gryaznov
"""
from pages.base_page import BasePage
from selenium.webdriver.common.by import By
import urllib
from selenium.webdriver.support import expected_conditions as EC
from helpers.driver_helper import DriverHelper

class SearchPage(BasePage):
    LISTING_LINKS = (By.CSS_SELECTOR, ".srp-results .s-item .s-item__link")
    LISTING_DATES = (By.CSS_SELECTOR, ".s-item__listingDate")
    NUMBER_OF_LISTINGS_PRO_PAGE = (By.CSS_SELECTOR, ".srp-ipp .expand-btn__cell span")
    NEXT_PAGE_BUTTON = (By.CSS_SELECTOR, ".pagination__next")
    
    @staticmethod
    def open_it_via_url(search_term):
        # TODO: remover hardcoded link and move parameters to config
        # here is hardcoded link for search with parameters:
        # -sale type: Sofort-kaufen
        # -state: Gebraucht
        # -sorting: by publishing date (new first)
        # -category: Handy & Smartphone
        SEARCH_LINK_PHONE = "https://www.ebay.de/sch/i.html?_from=R40&_nkw={search_term}&_sacat=9355&LH_BIN=1&_sop=10&rt=nc&LH_ItemCondition=3000&_ipg=200"
        
        driver = DriverHelper().get_driver()
        driver.get(SEARCH_LINK_PHONE.format(search_term=search_term))
        return SearchPage()
        
        
    def __init__(self):
        super(SearchPage, self).__init__()
        self.wait_for_element_to_be_visible(self.NUMBER_OF_LISTINGS_PRO_PAGE)
    
    # TODO: implement and add after opening page
    #def assert_search_page_opened_with_expected_search_parameters():
    
    def get_listing_links_and_dates(self): 
        listing_links = self.get_all_elements(self.LISTING_LINKS)
        listing_dates = self.get_all_elements(self.LISTING_DATES)
        assert len(listing_links) == len(listing_dates)
        print("number of listings on the page is {0}".format(len(listing_links)))
        return [{"link" : listing_links[i].get_attribute("href"), "date": listing_dates[i].text} for i in range(0, len(listing_links))]
    
    # it returns there_are_more_pages boolean
    def go_to_the_next_page_if_available(self):
        if self.is_element_visible(self.NEXT_PAGE_BUTTON):
            self.click_on_element(self.NEXT_PAGE_BUTTON)
            SearchPage()
            return True
        else:
            return False
    