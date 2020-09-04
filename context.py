#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Context:
    __instance = None
    driver = None
    mongo_collection = None
    mongo_client = None
    
    @staticmethod
    def getInstance():
        if Context.__instance == None:
            Context()
        return Context.__instance
    
    def __init__(self):
        if Context.__instance != None:
            raise Exception("Context is a singleton!")
        else:
            Context.__instance = self