#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 23:30:31 2018

@author: yuluo
"""

import abc

class ResourceABC(metaclass = abc.ABCMeta):
    
    @abc.abstractmethod
    def readFile(self, yamlFile):
        """
        read the content from yaml file
        :param yamlFile: the yaml file path
        :return: a list of cluster information
        """
        pass
    
    @abc.abstractmethod
    def add(self, content, filePath):
        """
        add new cluster content into the default yaml file
        :param content: new cluster content
        """
        pass
    
    @abc.abstractmethod
    def listAll(self, content):
        """
        print cluster information
        :param content: the cluster content in yaml file
        """
        pass
    
    @abc.abstractmethod
    def remove(self, content, filePath):
        """
        remove specified cluster contetn from yaml file
        :param content: the cluster content we have
        :param filePath: the file path of cotent that we want to remove
        """
        pass
    
    @abc.abstractmethod
    def updateFile(newContent):
        """
        update the cluster information into yaml file
        :param newContent: the new cluster information
        """
        pass
    