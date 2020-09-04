#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Saving new listings
# do it in parallel for different devices

import actions.actions as actions
import helpers.data_helper as data_helper

products = data_helper.get_products()

actions.scrape_new_listings(products[0])
#Parallel(n_jobs=8, verbose=1, backend="threading")(map(delayed(scrape_one_page), page_numbers))
