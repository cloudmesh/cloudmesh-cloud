#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 17:02:23 2018

@author: yuluo
"""

import yaml

class Config(object):
    
    def __init__(self, debug=False):
        '''
        initializes the configration for awscm
        
        :param debug: enables debug information to be printed
        '''
        
        self.debug = debug
        self.yaml = "/Users/yuluo/Desktop/cloudmesh.yaml"
        self._conf = {}
        
    def config(self):
        '''
        read the yaml file
        '''
        
        with open(self.yaml, "r") as stream:
            try:
                self._conf = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)    
        
    def get_default(self):
        '''
        ingest the default information
        
        :return default: the content in default block
        '''
        
        default = self._conf.get('cloudmesh').get('default')
        return default
    
    def get_cloud(self):
        '''
        ingest the cloud information
        
        :return cloud: the content in cloud block
        '''
        
        cloud = self._conf.get('cloudmesh').get('cloud')
        return cloud
    
    def get_cluster(self):
        '''
        ingest the cluster information
        
        :return cluster: the content in cluster block
        '''
        
        cluster = self._conf.get('cloudmesh').get('cluster')
        return cluster
    
    def get_config(self):
        '''
        ingest the content of yaml file
        
        :return conf: all information in yaml file
        '''
        
        return self._conf
    
    