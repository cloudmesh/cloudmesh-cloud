# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 11:48:09 2018

@author: Rui
"""

from cm4.vm.Cmaws import Cmaws
from cm4.vm.CmAzure import CmAzure
from cm4.vm.Cmopenstack import Cmopenstack
from cm4.configuration.config import Config
from cm4.cmmongo.mongoDB import MongoDB
from cm4.configuration.name import Name
from cm4.vm.thread import thread
from cm4.configuration.counter import Counter

class VmUtil(object):

    @staticmethod
    def _get_obj_list(self, obj_type):
        if obj_type == 'node':
            obj_list = self.driver.list_nodes()
        elif obj_type == 'image':
            obj_list = self.driver.list_images()
        elif obj_type == 'size':
            obj_list = self.driver.list_sizes()

        return obj_list


    @staticmethod
    def _get_obj_by_name(self, obj_type, obj_name):
        obj_list = self._get_obj_list(obj_type)
        for o in obj_list:
            if o.name == obj_name:
                return o


    @staticmethod
    def _get_obj_by_id(self, obj_type, obj_id):
        obj_list = self._get_obj_list(obj_type)
        for o in obj_list:
            if o.id == obj_id:
                return o


    @staticmethod
    def _get_node_by_id(self, node_id):
        return self._get_obj_by_id('node', node_id)


    @staticmethod
    def get_node_by_id(self, node_id):
        return VmUtil._get_obj_by_id('node', node_id)

