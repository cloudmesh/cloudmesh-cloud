#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 01:15:28 2018

@author: yuluo
"""

from pymongo import MongoClient
import urllib.parse

class MongoDB(object):
    #haven't tested it
    
    def __init__(self, port, username, password):
        self.database = 'cloudmesh'
        self.username = urllib.parse.quote_plus(username)
        self.port = port
        self.password = urllib.parse.quote_plus(password)
        self.client = MongoClient('mongodb://%s:%s@127.0.0.1:%s' % (self.username, self.password, self.port))
        self.db = self.client[self.database]
        
        
        
    def insert_instance_collection(self, document):
        instance = self.db['instance']    
        post_id = instance.insert_one(document).inserted_id
        return(post_id)
    

    def insert_cm_collection(self, document):
        cm = self.db['cm']
        post_id = cm.insert_one(document).inserted_id
        return(post_id)   
        
    
    def insert_status_collection(self):
        status = self.db['status']
        post_id = status.insert_one(document).inserted_id
        return(post_id)
        
    
    def insert_job_collection(self, document):
        job = self.db['job']
        post_id = job.insert_one(document).inserted_id
        return(post_id)
        
        
    def insert_group_collection(self, document):
        group = self.db['group']
        post_id = group.insert_one(document).inserted_id
        return(post_id)
        
    def update_document(self, collection_name, ID, info):
        collection = self.db[collection_name]
        result = collection.update_one({'_id' : ID}, {'$set' : info}).acknowledged
        return(result)
        
    def find_document(self, collection_name, key, value):
        collection = self.db[collection_name]
        document = collection.find({key : value})
        return(document)
        
    def delete_document(self, collection_name, ID):
        collection = self.db[collection_name]
        old_document = collection.find_one_and_delete({'_id' : ID})
        return(old_document)
         
        
    
    def instance_document(self, label, cloud, name, os='Null', memory='Null', 
                            storage='Null',address='Null', credential_id, credential_key, groupID='Null'):
        document = {'label' : label,
                        'cloud' : cloud,
                        'name' : name,
                        'spec' : {'os' : os,
                                      'cpu' : cpu,
                                      'memory' : memory,
                                      'storage' : storage},
                        'address' : address,
                        'credential' : {'id' : credential_id,
                                            'key' : credential_key},
                        'group' : groupID                            
                        }
        return(document)
    
        
    def cm_document(self, cloud, groupID, last_group):
        document = {'cloud' : cloud,
                    'group' : groupID,
                    'lastGroup' : last_group}
        return(document)
        
              
    def status_document(self, instanceID, status, jobID, history):
        document = {'_id' : instanceID,
                    'status' : status,
                    'currentJob' : jobID,
                    'history' : history}
        return(document)
        
         
    def job_document(self, name, status, inputInfo, outputInfo,
                               description='Null', commands):
        document = {'name' : name,
                    'status' : status,
                    'input' : inputInfo,
                    'output' : outputInfo,
                    'description' : description,
                    'commands' : commands}
        return(document)
        
        
    def group_document(self, cloud, name, size, list_vms):
        document = {'cloud' : cloud,
                    'name' : name,
                    'size' : size,
                    'vms' : list_vms}
        return(document)
        
   
        
    def close_client(self):
        self.client.close()
    
    
    