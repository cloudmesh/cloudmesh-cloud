#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 00:01:15 2018

@author: yuluo
"""

import abc

class ProcessABC(metaclass = abc.ABCMeta):
    
    @abc.abstractmethod
    def get_computer_list(self, yamlFile):
        """
        get the list of computers
        :param content: the yaml file content
        :return: a list of computer information
        """
        pass
    
    @abc.abstractmethod
    def get_computer(self, info):
        """
        get a specified computer information or randomly get a computer information
        :param info: name or label or empty
        :return: the computer key, username and public key
        """
        pass
    
    @abc.abstractmethod
    def run_remote(self, username, publickey, script):
        """
        run the script from remote machine
        :param username: the username of the vm
        :param publickey: the public key to access vm
        :param script: the script that would be run in vm
        :return: the result of runnng script
        """
        pass
    
    @abc.abstractmethod
    def scp(self, username, publickey, script):
        """
        copy the script to remote machine
        :param username: the username of the vm
        :param publickey: the public key to access vm
        :param script: the script that would be run in vm
        :return: location of the script in vm
        """
        pass
    
    @abc.abstractmethod
    def delete(self, username, publickey, file):
        """
        delete the script from remote machine
        :param username: the username of the vm
        :param publickey: the public key to access vm
        :param file: the location of script
        """
        pass
    
    @abc.abstractmethod
    def run_local(self, username, publickey, script):
        """
        run the script from local machine into remote machine
        :param username: the username of the vm
        :param publickey: the public key to access vm
        :param script: the script that would be run in vm
        :return: the result of runnng script
        """
        pass
    
    @abc.abstractmethod
    def parall_list(self, scripts):
        """
        get the list of computers that would run the scripts in parall
        :param scripts: the list of scripts
        :return: the list of computers that would run scripts
        """
        pass
    
    @abc.abstractmethod
    def run_parall(self, scripts):
        """
        run the scripts in parall in list of computers
        :param scripts: list of scripts
        :rerurn: the result of all scripts
        """
        pass
    
    @abc.abstractmethod
    def readable(self, result):
        """
        parse the result to readable format
        :param result: the result of parall processes
        """
        pass