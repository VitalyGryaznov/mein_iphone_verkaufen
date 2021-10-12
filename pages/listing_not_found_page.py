#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pages.base_page import BasePage
from selenium.webdriver.common.by import By
from models.phone_listing import PhoneListing
from helpers.driver_helper import DriverHelper


class ListingNotFoundPage(BasePage):
    
    NOT_FOUND = (By.CSS_SELECTOR, ".main-content .error-header__headline")
    
    def __init__(self):
        super(ListingNotFoundPage, self).__init__()
        self.wait_for_element_to_be_visible(self.NOT_FOUND)