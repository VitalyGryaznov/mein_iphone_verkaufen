#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pages.base_page import BasePage
from selenium.webdriver.common.by import By
from models.phone_listing import PhoneListing
from helpers.driver_helper import DriverHelper


class ListingPage(BasePage):
    
    TITLE = (By.CSS_SELECTOR, "#itemTitle")
    CHARACTERISTICS_TABLE_BASE_LOCATOR = "//*[contains(@class,'ux-layout-section--features')]//span[text()[contains(.,'{parameter}')]]/ancestor::div[@class='ux-labels-values__labels']/following-sibling::div[1]"
    ##CHARACTERISTICS_TABLE_BASE_LOCATOR = "//*[@class='itemAttr']//td[contains(text(),'{parameter}')]/following-sibling::td[1]"
    MODEL = (By.XPATH, CHARACTERISTICS_TABLE_BASE_LOCATOR.format(parameter="Modell:"))
    MEMORY = (By.XPATH, CHARACTERISTICS_TABLE_BASE_LOCATOR.format(parameter="Speicherkapazität:"))
    COLOR = (By.XPATH, CHARACTERISTICS_TABLE_BASE_LOCATOR.format(parameter="Farbe:"))
    CONDITION = (By.XPATH, "//*[contains(@class,'ux-layout-section--condition')]//span[text()[contains(.,'Artikelzustand:')]]/ancestor::div[@class='ux-labels-values__labels']/following-sibling::div[1]" + " | " + CHARACTERISTICS_TABLE_BASE_LOCATOR.format(parameter="Artikelzustand:"))
    MOBILE_OPERATOR = (By.XPATH, CHARACTERISTICS_TABLE_BASE_LOCATOR.format(parameter="Mobilfunkbetreiber:"))
    PRICE = (By.CSS_SELECTOR, "#prcIsum, #prcIsum_bidPrice, .vi-VR-cvipPrice, #mm-saleDscPrc")
    LISTING_ID = (By.CSS_SELECTOR, "#descItemNumber")
    SHIPPING_COST = (By.CSS_SELECTOR, "#fshippingCost")
    DESCRIPTION_IFARME = (By.CSS_SELECTOR, "#desc_ifr")
    BODY = (By.CSS_SELECTOR, "body")
    RETURN_POLICY = (By.CSS_SELECTOR, "#vi-ret-accrd-txt")
    NUMBER_OF_REVIEWS = (By.XPATH, "//a[contains(@title,'Bewertungspunktestand')] | //a[contains(@aria-label,'Bewertungspunktestand')]")
    EBAY_PLUS = (By.CSS_SELECTOR, ".sh-eplus-img")
    SELERS_FEETBACK = (By.CSS_SELECTOR, "#si-fb")
    PHOTOS_FROM_SLIDER = (By.CSS_SELECTOR, "#vi_main_img_fs_slider img")
    MAIN_IMAGE = (By.CSS_SELECTOR, "#icImg")
    CLOSURE_REASON = (By.CSS_SELECTOR, "#msgPanel .yellow .statusContent") #important to keep 'yellow' here, because empty '#msgPanel .statusContent' also presented on the new listing page  //div[@class='itemcard--content']//span[contains(text(),"beendet")]
    CLOSURE_DATE = (By.CSS_SELECTOR, "#bb_tlft")
    CLOSURE_DATE_ON_CLOSED_LISTING_WITH_RECOMENDATION = (By.XPATH, "//span[contains(text(), 'Beendet')]/ancestor::div[contains(@class,'nodestar-item-card-details__condition-cell')]/following-sibling::div//span")
    SHIPPING_FREE_OPTION = (By.CSS_SELECTOR, "#fShippingSvc")
    ORIGINAL_LISTING_LINK = (By.XPATH, "//a[contains(text(),'Originalartikel ansehen')] | //section[contains(@class, 'page-notice--information')]//a//img")
    ORIGINAL_LISTING_LINK_V2 = (By.XPATH, "//a[contains(text(),'Originalangebot aufrufen')]")
    NUMBER_OF_ITEMS_IN_SALE = (By.CSS_SELECTOR, "#qtySubTxt")
    
    
    def __init__(self):
        super(ListingPage, self).__init__()
        # wait_for_one_element_to_be_presented needed, because sometimes we are opening page for sold product with suggested product info
        # It would make sence to have several classes for 3 potentials staes of the listing page (active/not active with info about product/not active with link to the product),
        # but I'm not doing it now to keep it simple
        self.wait_for_one_element_to_be_presented(self.TITLE, self.ORIGINAL_LISTING_LINK)
        self.wait_for_one_element_to_be_presented(self.LISTING_ID, self.ORIGINAL_LISTING_LINK)
        self.wait_for_one_element_to_be_presented(self.NUMBER_OF_REVIEWS, self.ORIGINAL_LISTING_LINK)
                
    @staticmethod
    def open_url_in_the_new_tab(link):
        DriverHelper().open_url_in_the_new_tab(link)
        return ListingPage()
    
    @staticmethod
    def open_url(link):
        driver = DriverHelper().get_driver()
        driver.get(link)
        return ListingPage()
    
    def open_original_listing_if_the_link_is_available(self):
        if self.is_element_visible(self.ORIGINAL_LISTING_LINK):
            self.click_on_element(self.ORIGINAL_LISTING_LINK)
        elif self.is_element_visible(self.ORIGINAL_LISTING_LINK_V2):
            self.click_on_element(self.ORIGINAL_LISTING_LINK_V2)
        else:
            print("No 'original  listing' link presented")
                                   

    def the_link_to_the_closed_listing_is_available(self):
        return self.is_element_visible(self.ORIGINAL_LISTING_LINK)
    
    def get_listing_data(self):
        listing = PhoneListing()
        listing.link = self.driver.current_url
        listing.title = self.wait_for_element_and_get_text(self.TITLE)
        listing.text_description = self.get_text_description()
        listing.price = self.get_price()
        listing.return_policy = self.wait_for_element_and_get_text(self.RETURN_POLICY)
        listing.shipping_cost = self.get_shipping_cost()
        listing._id = self.wait_for_element_and_get_text(self.LISTING_ID)
        listing.number_of_reviews = self.wait_for_element_and_get_text(self.NUMBER_OF_REVIEWS)
        listing.photos = self.get_photos()
        listing.multiple_items_available = self.is_element_visible(self.NUMBER_OF_ITEMS_IN_SALE)
        
        #optional parameters
        listing.model = self.get_optionl_characteristic_value(self.MODEL)
        listing.memory = self.get_optionl_characteristic_value(self.MEMORY)
        listing.color = self.get_optionl_characteristic_value(self.COLOR)
        listing.condition = self.get_optionl_characteristic_value(self.CONDITION)
        listing.mobile_operator = self.get_optionl_characteristic_value(self.MOBILE_OPERATOR)
        listing.selers_feedback = self.get_optionl_characteristic_value(self.SELERS_FEETBACK)
        return listing
        
    def get_text_description(self):
        self.driver.switch_to.frame(self.wait_for_element_to_be_visible(self.DESCRIPTION_IFARME))
        try:
            text = self.wait_for_element_and_get_text(self.BODY)
        finally:
            self.driver.switch_to.default_content()
        return text
    
    def get_photos(self):
        main_image = self.wait_for_element_to_be_visible(self.MAIN_IMAGE)
        #sometimes there is only one image
        if self.is_element_visible(self.PHOTOS_FROM_SLIDER):
            photos = self.get_all_elements(self.PHOTOS_FROM_SLIDER)
            photos_links = []
            for photo in photos:
                photos_links.append(photo.get_attribute("src").replace("s-l64", "s-l300"))
            return photos_links
        else:
            return [main_image.get_attribute("src")]
    
    # some characteristics are not presented in rare cases
    def get_optionl_characteristic_value(self, locator):
        return self.wait_for_element_and_get_text(locator) if self.is_element_visible(locator) else None
        
    def is_active(self):
        return not (self.is_element_visible(self.CLOSURE_REASON) or self.is_element_visible(self.ORIGINAL_LISTING_LINK))
    
    def get_closure_reason(self):
        return self.wait_for_element_and_get_text(self.CLOSURE_REASON)
    
    def get_price(self):
        return self.wait_for_element_and_get_text(self.PRICE)
    
    def get_shipping_cost(self):
        if self.is_element_visible(self.SHIPPING_COST):
            return self.wait_for_element_and_get_text(self.SHIPPING_COST)
        elif self.is_element_visible(self.SHIPPING_FREE_OPTION):
            return self.wait_for_element_and_get_text(self.SHIPPING_FREE_OPTION)
        else:
            return None

    def get_closure_date(self):
        if self.is_element_visible(self.CLOSURE_DATE_ON_CLOSED_LISTING_WITH_RECOMENDATION):
            return self.wait_for_element_and_get_text(self.CLOSURE_DATE_ON_CLOSED_LISTING_WITH_RECOMENDATION)
        else:
            return self.wait_for_element_and_get_text(self.CLOSURE_DATE)
        