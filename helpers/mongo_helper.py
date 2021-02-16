#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from models.phone_listing import PhoneListing
from pymongo import MongoClient
from context import Context

class MongoHelper(object):
    
   
    #it would be nice to move those constants to config later
    COLLECTION_NAME = 'iphones'
    DB_NAME = 'ebay'
    CONNECTION_HOST = 'localhost'
    CONNECTION_PORT = 27017
    
    def start_client_and_connect(self):
        client = MongoClient(self.CONNECTION_HOST, self.CONNECTION_PORT)
        db = client[self.DB_NAME]
        Context.getInstance().mongo_client = client
        Context.getInstance().mongo_collection = db[self.COLLECTION_NAME]
    
    def close_connection(self):
        Context.getInstance().mongo_client.close()
                                                                  
    def get_collection(self):
        return Context.getInstance().mongo_collection                                                              

    def get_listing_by_id(self, listing_id):
        collection = self.get_collection()                                            
        listing = list(collection.find({"_id": listing_id}))
        return listing
    
    def get_active_listings(self, search_term):
        collection = self.get_collection()
        return collection.find({"active": True, "search_term": search_term})
    
    def get_active_and_not_flaged_as_old_listings(self, search_term):
        collection = self.get_collection()
        # {"$exists": False} is correct. We don't have this value by default. Adding True value in case it's old
        return collection.find({"active": True, "search_term": search_term, "old": {"$exists": False}})    
    
    def get_active_singleitem_and_not_flaged_as_old_listings(self, search_term):
        collection = self.get_collection()
        return collection.find({"active": True, "search_term": search_term, "old": {"$exists": False}, "multiple_items_available": False})   
    
    def insert_one(self, post):
        self.get_collection().insert_one(post)
    
    def insert_listing(self, listing):
        self.insert_one(vars(listing))
    
    def update_listing(self, listing_id, key, value):
        self.get_collection().update_one({"_id": listing_id}, {"$set": {key: value}})
