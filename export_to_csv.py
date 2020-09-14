#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
import pandas as pd
from pymongo import MongoClient
client = MongoClient()
db = client.ebay
collection = db.iphones
data = pd.DataFrame(list(collection.find()))
data.to_csv('iphones.csv', index=False, header=True, sep=";")