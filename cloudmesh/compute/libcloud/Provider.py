from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from pprint import pprint
from datetime import datetime
from cloudmesh.common.util import HEADING

from cloudmesh.management.configuration.config import Config

from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider as LibcloudProvider


class Provider(ComputeNodeABC):

    ProviderMapper = {"openstack": LibcloudProvider.OPENSTACK,
                      "aws": LibcloudProvider.EC2}

    def __init__(self, name=None, configuration="~/.cloudmesh/cloudmesh4.yaml"):
        HEADING(c=".")
        conf = Config(configuration)["cloudmesh"]
        mycloud = conf["cloud"][name]
        cred = mycloud["credentials"]
        cloudkind = mycloud["cm"]["kind"]
        #pprint (cred)
        #print (cloudkind)
        super().__init__(name, conf)
        if cloudkind in Provider.ProviderMapper:
            if cloudkind == 'openstack':
                self.driver = get_driver(Provider.ProviderMapper[cloudkind])
                self.cloudman = self.driver(cred["OS_USERNAME"],
                                    cred["OS_PASSWORD"],
                                    ex_force_auth_url=cred['OS_AUTH_URL'],
                                    ex_force_auth_version='2.0_password',
                                    ex_tenant_name=cred['OS_TENANT_NAME'])
        else:
            print ("Specified provider not available")
            self.cloudman = None
        self.default_image = None
        self.default_size = None
        self.public_key_path = conf["profile"]["key"]["public"]

    def start(self, name):
        """
        start a node
    
        :param name: the unique node name
        :return:  The dict representing the node
        """
        HEADING(c=".")

    def stop(self, name=None):
        """
        stops the node with the given name
    
        :param name:
        :return: The dict representing the node including updated status
        """
        HEADING(c=".")

    def info(self, name=None):
        """
        gets the information of a node with a given name
    
        :param name:
        :return: The dict representing the node including updated status
        """
        HEADING(c=".")

    def suspend(self, name=None):
        """
        suspends the node with the given name
    
        :param name: the name of the node
        :return: The dict representing the node
        """
        HEADING(c=".")

    def list(self):
        """
        list all nodes id
    
        :return: an array of dicts representing the nodes
        """
        HEADING(c=".")
        if self.cloudman:
            return (self.cloudman.list_nodes())

    def resume(self, name=None):
        """
        resume the named node
    
        :param name: the name of the node
        :return: the dict of the node
        """
        HEADING(c=".")

    def destroy(self, name=None):
        """
        Destroys the node
        :param name: the name of the node
        :return: the dict of the node
        """
        HEADING(c=".")

    def create(self, name=None, image=None, size=None, timeout=360, **kwargs):
        """
        creates a named node
    
        :param name: the name of the node
        :param image: the image used
        :param size: the size of the image
        :param timeout: a timeout in seconds that is invoked in case the image does not boot.
               The default is set to 3 minutes.
        :param kwargs: additional arguments HEADING(c=".")ed along at time of boot
        :return:
        """
        """
        create one node
        """
        HEADING(c=".")

    def rename(self, name=None, destination=None):
        """
        rename a node
    
        :param destination:
        :param name: the current name
        :return: the dict with the new name
        """
        # if destination is None, increase the name counter and use the new name
        HEADING(c=".")
