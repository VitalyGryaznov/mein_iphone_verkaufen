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
        return collection.find({"active": True})
    
    def insert_one(self, post):
        self.get_collection().insert_one(post)
    
    def insert_listing(self, listing):
        self.insert_one(vars(listing))
    
    def update_listing(self, listing_id, key, value):
        self.get_collection.update_one({"_id": listing_id}, {"$set": {key: value}})

    #NOT USED:

    def exists_advert(self, advert_id):
        mydoc = list(self.collection.find({"_id": advert_id}))
        return len(mydoc) > 0
    
    

    def update_field_changed(self, key, advert, date):
        if self.get_advert_with_id(advert.advert_id)[0][key][-1][key] != getattr(advert, key):
            self.collection.update_one({"_id": advert.advert_id}, {"$push": {key: {key: getattr(advert, key), "date": date}}})

    def set_advert_inactive(self, advert_id, date):
        self.collection.update_one({"_id": advert_id}, {"$set": {"active": False}})
        self.collection.update_one({"_id": advert_id}, {"$set": {"closed_date": date}})
    
    def add_data_if_changed(self, advert, date):
        keys = ["number_of_photos", "short_title", "full_title", "price", "short_descr", "top_lable", "description", "number_of_views", "pro_lable"]
        for key in keys:
            self.update_field_changed(key, advert, date)
            
    def add_data_if_changed_only_for_detiled_description(self, advert, date):
        keys = ["number_of_photos", "full_title", "price", "description", "number_of_views"]
        for key in keys:
            self.update_field_changed(key, advert, date)
        
    def close_client(self):
        self.client.close()
    
    def get_all_active_adverts(self):
        return self.collection.find({"active": True})
    
        
