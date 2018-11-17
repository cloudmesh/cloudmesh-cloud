# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 23:58:09 2018

@author: Rui
"""

from cm4.abstractclass.CloudManagerABC import CloudManagerABC
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import os
from cm4.configuration.config import Config


class VmRefactor(object):
    def __init__(self, driver):
        pass

    # resize request need additional confirmation in openstack
    def confirm_resize(self, node_id):
        '''
        confirm a resizing request for a node
        :param: node_id,
        :return: bool
        '''
        node = self.cm._get_node_by_id(node_id)
        return self.cm.driver.ex_confirm_resize(node)


    def resize(self, node_id, size):
        '''
        resize a node
        :param: node_id, new size object
        :return: bool
        '''
        node = self.cm._get_node_by_id(node_id)
        return self.cm.driver.ex_resize(node, size)


    def revert_resize(self, node_id):
        '''
        revert previous resize request
        :param: node_id
        :return: bool
        '''
        node = self.cm._get_node_by_id(node_id)
        return self.cm.driver.ex_revert_resize(node)


    # rebuild node with new image
    def rebuild(self, node_id, image):
        '''
        refactor node to a different image
        :param: node id, new image object
        :return: Node
        '''
        node = self.cm._get_node_by_id(node_id)
        return self.cm.driver.ex_rebuild(node, image=image)


    def rename(self, node_id, name):
        '''
        rename a node by its id
        :param: name: new name for node
        :return: Node
        '''
        node = self.cm._get_node_by_id(node_id)
        return self.cm.driver.ex_set_server_name(node, name)


    ## util
    def get_node_by_id(self, node_id):
        '''
        get node object by id string
        :param:node id
        :return: node object
        '''
        return self._get_obj_by_id('node', node_id)