#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml

IPHONES_SPEC_PATH = "resources/iphone_specs.yaml"

def read_file(filename):
    file = open(filename)
    data = yaml.load(file, Loader=yaml.FullLoader)
    file.close()
    return data
    
def get_products():
    return read_file(IPHONES_SPEC_PATH)["products"]
