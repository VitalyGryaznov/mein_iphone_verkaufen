#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import actions.actions as actions
import helpers.data_helper as data_helper

products = data_helper.get_products()


actions.check_active_listings(products[0])