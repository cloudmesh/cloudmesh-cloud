#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 23:30:31 2018

@author: yuluo
"""

import abc


# noinspection PyPep8Naming
class ResourceABC(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def readFile(self, yaml_file):
        """
        read the content from yaml file
        :param yaml_file: the yaml file path
        :return: a list of cluster information
        """
        pass

    @abc.abstractmethod
    def add(self, content, file_path):
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
    def remove(self, content, file_path):
        """
        remove specified cluster contetn from yaml file
        :param content: the cluster content we have
        :param file_path: the file path of cotent that we want to remove
        """
        pass

    @abc.abstractmethod
    def updateFile(new_content):
        """
        update the cluster information into yaml file
        :param new_content: the new cluster information
        """
        pass
