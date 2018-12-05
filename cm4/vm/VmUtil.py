# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 11:48:09 2018

@author: Rui
"""


class VmUtil(object):

    @staticmethod
    def _get_obj_list(self, obj_type):
        obj_list = []

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
        return self._get_obj_by_id('node', node_id)
