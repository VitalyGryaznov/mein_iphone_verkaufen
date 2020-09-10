#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from context import Context
from helpers.driver_helper import DriverHelper
from selenium.common.exceptions import TimeoutException


class BasePage(object):
    def __init__(self):
        self.driver = DriverHelper().get_driver()
        self.wait = WebDriverWait(self.driver, 30)

    def wait_for_element_to_be_visible(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))
    
    def is_element_visible(self, locator):
        # this method is waiting for the element to appear only 2 seconds
        # It's done to speed up script
        # This method could be used only when you are 100% sure that page elready loaded
        wait = WebDriverWait(self.driver, 2)
        try:
            wait.until(EC.presence_of_element_located(locator))
            return True
        except TimeoutException:
            return False 
    
    def wait_for_element_and_get_text(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator)).text
    
    def click_on_element(self, locator):
        print("clicking on element with locator: {0} {1}".format(locator[0], locator[1]))
        element = self.wait.until(EC.presence_of_element_located(locator))
        self.driver.execute_script("arguments[0].click();", element)
        
    def get_all_elements(self, locator):
        return self.driver.find_elements(locator[0], locator[1])
        