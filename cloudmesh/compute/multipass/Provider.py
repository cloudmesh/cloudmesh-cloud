from abc import ABCMeta, abstractmethod
from cloudmesh.configuration.Config import Config

from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC


#
# Implement functions related to vm management
#
# Do not woryy about implementing key and
# secgroup at this time
#
# We marked the methods to be implemented with
# # IMPLEMENT ME
#

class Provider(ComputeNodeABC):

    # IMPLEMENT ME
    def __init__(self, name=None, configuration="~/.cloudmesh/cloudmesh.yaml"):
        """
        Initializes the provider. The default parameters are read from the
        configuration file that is defined in yaml format.

        :param name: The name of the provider as defined in the yaml file
        :param configuration: The location of the yaml configuration file
        """

        self.conf = Config(configuration)["cloudmesh"]
        super().__init__(name, self.conf)

        self.user = Config()["cloudmesh"]["profile"]["user"]
        self.spec = self.conf["cloud"][name]
        self.cloud = name

        self.default = self.spec["default"]
        self.cloudtype = self.spec["cm"]["kind"]

        self.cred = self.spec["credentials"]

        #
        # TODO: additional code to be added here
        #

    # IMPLEMENT ME
    def start(self, name=None):
        """
        start a node

        :param name: the unique node name
        :return:  The dict representing the node
        """
        raise NotImplementedError

    # IMPLEMENT ME
    def stop(self, name=None):
        """
        stops the node with the given name

        :param name:
        :return: The dict representing the node including updated status
        """
        raise NotImplementedError

    # IMPLEMENT ME
    def info(self, name=None):
        """
        gets the information of a node with a given name

        :param name:
        :return: The dict representing the node including updated status
        """
        raise NotImplementedError

    # IMPLEMENT ME
    def suspend(self, name=None):
        """
        suspends the node with the given name

        :param name: the name of the node
        :return: The dict representing the node
        """
        raise NotImplementedError

    # IMPLEMENT ME
    def list(self, **kwargs):
        """
        list all vms

        :return: an array of dicts representing the nodes
        """
        raise NotImplementedError

    # IMPLEMENT ME
    def resume(self, name=None):
        """
        resume the named node

        :param name: the name of the node
        :return: the dict of the node
        """
        raise NotImplementedError

    # IMPLEMENT ME
    def destroy(self, name=None):
        """
        Destroys the node
        :param name: the name of the node
        :return: the dict of the node
        """
        raise NotImplementedError

    # IMPLEMENT ME
    def create(self,
               name=None,
               image=None,
               size=None,
               timeout=360,
               group=None,
               **kwargs):
        """
        creates a named node

        :param group: a list of groups the vm belongs to
        :param name: the name of the node
        :param image: the image used
        :param size: the size of the image
        :param timeout: a timeout in seconds that is invoked in case the image does not boot.
               The default is set to 3 minutes.
        :param kwargs: additional arguments passed along at time of boot
        :return:
        """
        """
        create one node
        """
        raise NotImplementedError

    # IMPLEMENT ME
    def set_server_metadata(self, name, **metadata):
        """
        sets the metadata for the server

        :param name: name of the fm
        :param metadata: the metadata
        :return:
        """
        raise NotImplementedError

    # IMPLEMENT ME
    def get_server_metadata(self, name):
        """
        gets the metadata for the server

        :param name: name of the fm
        :return:
        """
        raise NotImplementedError

    
    def delete_server_metadata(self, name):
        """
        gets the metadata for the server

        :param name: name of the fm
        :return:
        """
        raise NotImplementedError

    # IMPLEMENT ME (can it be done?)
    def rename(self, name=None, destination=None):
        """
        rename a node

        :param destination:
        :param name: the current name
        :return: the dict with the new name
        """
        # if destination is None, increase the name counter and use the new name
        raise NotImplementedError

    def keys(self):
        """
        Lists the keys on the cloud

        :return: dict
        """
        raise NotImplementedError

    
    def key_upload(self, key=None):
        """
        uploads the key specified in the yaml configuration to the cloud
        :param key:
        :return:
        """
        raise NotImplementedError

    def key_delete(self, name=None):
        """
        deletes the key with the given name
        :param name: The name of the key
        :return:
        """
        raise NotImplementedError

    def images(self, **kwargs):
        """
        Lists the images on the cloud
        :return: dict
        """
        raise NotImplementedError

    def image(self, name=None):
        """
        Gets the image with a given nmae
        :param name: The name of the image
        :return: the dict of the image
        """
        raise NotImplementedError

    def flavors(self, **kwargs):
        """
        Lists the flavors on the cloud

        :return: dict of flavors
        """
        raise NotImplementedError

    def flavor(self, name=None):
        """
        Gets the flavor with a given name

        :param name: The name of the flavor
        :return: The dict of the flavor
        """
        raise NotImplementedError

    # IMPLEMENT ME
    def reboot(self, name=None):
        """
        Reboot a list of nodes with the given names

        :param name: A list of node names
        :return:  A list of dict representing the nodes
        """
        raise NotImplementedError

    def attach_public_ip(self, name=None, ip=None):
        """
        adds a public ip to the named vm

        :param name: Name of the vm
        :param ip: The ip to attach to the vm
        :return:
        """
        raise NotImplementedError

    def detach_public_ip(self, name=None, ip=None):
        """
        adds a public ip to the named vm

        :param name: Name of the vm
        :param ip: The ip to attach to the vm
        :return:
        """
        raise NotImplementedError

    def delete_public_ip(self, ip=None):
        """
        Deletes the ip address

        :param ip: the ip address, if None than all will be deleted
        :return:
        """
        raise NotImplementedError

    def list_public_ips(self, available=False):
        """
        Lists the public ip addresses.

        :param available: if True only those that are not allocated will be
            returned.

        :return:
        """
        raise NotImplementedError

    def create_public_ip(self):
        """
        Creates a new public IP address to use

        :return: The ip address information
        """
        raise NotImplementedError

    def find_available_public_ip(self):
        """
        Returns a single public available ip address.

        :return: The ip
        """
        raise NotImplementedError

    def get_public_ip(self, name=None):
        """
        returns the public ip

        :param name: name of the server
        :return:
        """
        raise NotImplementedError

    def list_secgroups(self, name=None):
        """
        List the named security group

        :param name: The name of the group, if None all will be returned
        :return:
        """

    def list_secgroup_rules(self, name='default'):
        """
        List the named security group

        :param name: The name of the group, if None all will be returned
        :return:
        """
        raise NotImplementedError

    def upload_secgroup(self, name=None):
        raise NotImplementedError

    def list_secgroup_rules(self, name='default'):
        raise NotImplementedError

    def add_secgroup(self, name=None, description=None):
        raise NotImplementedError

    def add_secgroup_rule(self,
                          name=None,  # group name
                          port=None,
                          protocol=None,
                          ip_range=None):
        raise NotImplementedError

    def remove_secgroup(self, name=None):
        raise NotImplementedError

    def upload_secgroup(self, name=None):
        raise NotImplementedError

    def add_rules_to_secgroup(self, name=None, rules=None):
        raise NotImplementedError

    def remove_rules_from_secgroup(self, name=None, rules=None):
        raise NotImplementedError

    # IMPLEMENT ME (can it be done?)
    def wait(self,
             vm=None,
             interval=None,
             timeout=None):
        """
        wais till the given VM can be logged into

        :param vm: name of the vm
        :param interval: interval for checking
        :param timeout: timeout
        :return:
        """
        raise NotImplementedError
        return False

    # IMPLEMENT ME (can it be done?)
    def console(self, vm=None):
        """
        gets the output from the console

        :param vm: name of the VM
        :return:
        """
        raise NotImplementedError
        return ""

    # IMPLEMENT ME (can it be done?)
    def log(self, vm=None):
        raise NotImplementedError
        return ""
