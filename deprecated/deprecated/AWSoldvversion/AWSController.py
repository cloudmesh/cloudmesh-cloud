from cm4.abstractclass.ComputeNodeManagerABC import ComputeNodeManagerABC
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import json
from pprint import pprint


# for more information:
# https://libcloud.readthedocs.io/en/latest/apidocs/libcloud.compute.drivers.html#module-libcloud.compute.drivers.ec2


class AWSController(ComputeNodeManagerABC):

    def __init__(self, ACCESS_ID, SECRET_KEY, region):
        """
        initialize the AWS driver
        :param ACCESS_ID:
        :param SECRET_KEY:
        :param region:
        """
        cls = get_driver(Provider.EC2)
        self.driver = cls(ACCESS_ID, SECRET_KEY, region=region)

    def start(self, node_id):
        """
        start the node
        :param node_id:
        :return: True/False
        """
        nodes = self.driver.list_nodes()
        for i in nodes:
            if i.id == node_id:
                result = self.driver.ex_start_node(i)
                return result

    def ls(self):
        """
        list all nodes in AWS
        :return: list of id, name, state
        """
        nodes = self.driver.list_nodes()
        return [dict(id=i.id, name=i.name, state=i.state) for i in nodes]

    def info(self, node_id):
        """
        get clear information about one node
        :param node_id:
        :return: metadata of node
        """
        '''
        nodes = self.driver.list_nodes()
        for i in nodes:
            if i.id == node_id:
                return i
        '''
        return self.driver.list_nodes([node_id])

    def stop(self, node_id):
        """
        stop the node
        :param node_id:
        :return: True/False
        """
        nodes = self.driver.list_nodes()
        for i in nodes:
            if i.id == node_id:
                result = self.driver.ex_stop_node(i)
                return result

    def suspend(self, image_id):
        print('Cannot suspend the instance, only stop operation')

    def resume(self, image_id):
        print('Cannot resume the instance, only start operation')

    def destroy(self, node_id):
        """
        delete the node
        :param node_id:
        :return: True/False
        """
        nodes = self.driver.list_nodes()
        for i in nodes:
            if i.id == node_id:
                result = self.driver.destroy_node(i)
                return result

    def create(self, size, image, keyname, security):
        """
        create node
        :param security:
        :param keyname:
        :param image:
        :param size:
        :return:
        """
        # https://libcloud.readthedocs.io/en/latest/_modules/libcloud/compute/drivers/ec2.html#BaseEC2NodeDriver.create_node
        sizes = self.driver.list_sizes()
        images = self.driver.list_images()
        size = [s for s in sizes if s.id == size][0]
        image = [i for i in images if i.id == image][0]

        self.driver.create_node(name=None, image=image, size=size, ex_keyname=keyname, ex_securitygroup=security)

