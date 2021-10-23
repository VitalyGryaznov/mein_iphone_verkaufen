#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from context import Context
import os
import time

class DriverHelper(object):
    # this is driver path. by default it's path to mac driver. could be selected automaticly based on os, but it's out of scope here
    DRIVER_PATH = 'resources/chromedriver'
    
    def start_driver(self):
        # add executable to the path
        dirname = os.path.dirname(__file__)
        driver_path = os.path.join(dirname, self.DRIVER_PATH)
        
        # it would be nice to move chrome options and properties to yaml. out of scope for now
        options = Options()
        options.add_argument('--disable-gpu')
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--start-maximized')
        options.add_argument("--user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'")
        Context.getInstance().driver = webdriver.Chrome(executable_path=self.DRIVER_PATH, chrome_options=options)

    def quit_driver(self):
        driver = self.get_driver()
        if driver:
            driver.quit()
            driver = None
            
    def get_driver(self):
        return Context.getInstance().driver
    
    def open_url_in_the_new_tab(self, link):
        driver = self.get_driver()
        windows_before  = driver.current_window_handle
        driver.execute_script('''window.open("{}","_blank");'''.format(link))
        windows_after = driver.window_handles
        new_window = [x for x in windows_after if x != windows_before][0]
        driver.switch_to_window(new_window)
    
    def close_current_tab_and_go_to_the_first_one(self):
        driver = self.get_driver()
        driver.close()
        driver.switch_to.window(window_name=driver.window_handles[0])
        
    def take_screenshot(self, file_name = "screenshot"):
        screenshot_name = "{0}{1}.png".format(file_name, round(time.time() * 1000))
        try:
            self.get_driver().save_screenshot(screenshot_name)
            print("Screenshot saved {0}".format(screenshot_name))
        except Exception as e:
            print("Failed to make a screenshot")
            print(e)
