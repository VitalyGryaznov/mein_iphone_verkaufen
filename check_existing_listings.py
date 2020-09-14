#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import actions.actions as actions
import helpers.data_helper as data_helper
from joblib import Parallel, delayed

products = data_helper.get_products()

Parallel(n_jobs=3, verbose=1, backend='loky')(map(delayed(actions.check_active_listings), products))