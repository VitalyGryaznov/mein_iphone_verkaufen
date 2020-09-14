#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Saving new listings
# do it in parallel for different searcj=h terms

import actions.actions as actions
import helpers.data_helper as data_helper
from joblib import Parallel, delayed

products = data_helper.get_products()

Parallel(n_jobs=4, verbose=1, backend='loky')(map(delayed(actions.scrape_new_listings), products))