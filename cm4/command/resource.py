#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 23:57:04 2018

@author: yuluo
"""

from ResourceABC import ResourceABC
import yaml
import os

class Resource(ResourceABC):
    
    def __init__(self):
        # TODO:
        self.yamlFile = os.path.expanduser("~/.cloudmesh/cloudmesh.yaml")
        
    
    
    def readFile(self, yamlFile):
        cloudmesh = ""
        with open(yamlFile, "r") as stream:
            try:
                cloudmesh = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)    
        return cloudmesh
                
    
    
    def add(self, content, filePath):
        newContent = self.readFile(filePath)
        for i in newContent:
            ((content["cloudmesh"])["cluster"]).update({i:newContent[i]})
        self.updateFile(content)
        
    
    
    def listAll(self, content):
        computer = yaml.dump((content["cloudmesh"])["cluster"])
        print(computer)
        
    
    
    def remove(self, content, filePath):
        newContent = self.readFile(filePath)
        for i in newContent:
            del ((content["cloudmesh"])["cluster"])[i]
        self.updateFile(content)

    
    
    def updateFile(self, newContent):
        with open(self.yamlFile, "w") as output:
            yaml.dump(newContent,output)
