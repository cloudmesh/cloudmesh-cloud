from cm4.abstractclass.CloudManagerABC import CloudManagerABC
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import os
from config import Config

import libcloud.security

# This assumes you don't have SSL set up.
# Note: Code like this poses a security risk (MITM attack) and
# that's the reason why you should never use it for anything else
# besides testing. You have been warned.
libcloud.security.VERIFY_SSL_CERT = False

CHAMELEON_CLOUD_CHI = ""    # chameleon endpoint

class OpenstackCM (CloudManagerABC):

    def __init__(self, ACCESS_ID, SECRET_KEY, region):
        config = Config()
        self.os_config = config.get_cloud().get("openstack")
        self.driver = get_driver()      # init a default driver


    def get_driver(self, cloud):

        credential = self.os_config.get("credentials")

        Openstack = get_driver(Provider.OPENSTACK)
        driver = Openstack(
            credential.get('user'),
            credential.get('password'),
            ex_force_base_url=credential.get("url"),
            api_version=credential.get("api_version"),
            ex_tenant_name=credential.get("tennant_name") )
        return driver


    def start_node(self, node_id):
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
        nodes = self.driver.list_nodes()
        for i in nodes:
            if i.id == node_id:
                return dict(id=i.id, name=i.name, state=i.state, public_ips=i.public_ips, private_ips=i.private_ips,
                            size=i.size, image=i.image, created_date=i.created_at.strftime ("%Y-%m-%d %H:%M:%S"), extra=i.extra)

    def stop_node(self, node_id):
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

    def suspend_node(self, image_id):
        pass

    def resume_node(self, image_id):
        pass

    def destroy_nodes(self, node_id):
        """
        delete the node
        :param node_id:
        :return: True/False
        """
        nodes = self.driver.list_nodes()
        for i in nodes:
            if i.id == nodes:
                result = self.driver.destroy_node(i)
                return result

    def create_node(self, **kwargs):
        return self.driver.create_node(**kwargs)



#
if __name__ == "__main__":
    pass
