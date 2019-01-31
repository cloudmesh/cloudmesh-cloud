# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 2018

@author: Rui
"""


# noinspection PyProtectedMember
class OpenstackRefactor(object):
    def __init__(self, cm=None):
        self.cm = cm

    def list_sizes(self):
        """
        List sizes on a provider
        :param:
        :return: list of NodeSize
        """
        return self.cm.driver.list_sizes()

    def list_images(self, location=None, ex_only_active=True):
        """
        Lists all active images using the V2 Glance API
        :param:
        :return: list of Images
        """
        return self.cm.driver.list_images(location, ex_only_active)

    # resize request need additional confirmation in openstack
    def confirm_resize(self, node_id):
        """
        confirm a resizing request for a node
        :param: node_id,
        :return: bool
        """
        node = self.cm._get_node_by_id(node_id)
        return self.cm.driver.ex_confirm_resize(node)

    def resize(self, node_id, size):
        """
        resize a node
        :param: node_id, new size object
        :return: bool
        """
        node = self.cm._get_node_by_id(node_id)
        return self.cm.driver.ex_resize(node, size)

    def revert_resize(self, node_id):
        """
        revert previous resize request
        :param: node_id
        :return: bool
        """
        node = self.cm._get_node_by_id(node_id)
        return self.cm.driver.ex_revert_resize(node)

    # rebuild node with new image
    def rebuild(self, node_id, image):
        """
        refactor node to a different image
        :param: node id, new image object
        :return: Node
        """
        node = self.cm._get_node_by_id(node_id)
        return self.cm.driver.ex_rebuild(node, image=image)

    def rename(self, node_id, name):
        """
        rename a node by its id
        :param: name: new name for node
        :return: Node
        """
        node = self.cm._get_node_by_id(node_id)
        return self.cm.driver.ex_set_server_name(node, name)
