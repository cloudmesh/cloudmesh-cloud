from abc import ABCMeta, abstractmethod
from cloudmesh.management.configuration.config import Config


# noinspection PyUnusedLocal
class ComputeNodeABC(metaclass=ABCMeta):

    def __init__(self, cloud, path):
        config = Config(config_path=path)["cloudmesh"]
        self.cm = config["cloud"][cloud]["cm"]
        self.default = config["cloud"][cloud]["default"]
        self.credentials = config["cloud"][cloud]["credentials"]
        self.group = config["default"]["group"]
        self.experiment = config["default"]["experiment"]

    @abstractmethod
    def start(self, name=None):
        """
        start a node

        :param name: the unique node name
        :return:  The dict representing the node
        """
        raise NotImplementedError

    @abstractmethod
    def stop(self, name=None):
        """
        stops the node with the given name

        :param name:
        :return: The dict representing the node including updated status
        """
        raise NotImplementedError

    @abstractmethod
    def info(self, name=None):
        """
        gets the information of a node with a given name

        :param name:
        :return: The dict representing the node including updated status
        """
        raise NotImplementedError

    @abstractmethod
    def suspend(self, name=None):
        """
        suspends the node with the given name

        :param name: the name of the node
        :return: The dict representing the node
        """
        raise NotImplementedError

    @abstractmethod
    def list(self):
        """
        list all vms

        :return: an array of dicts representing the nodes
        """
        raise NotImplementedError

    @abstractmethod
    def resume(self, name=None):
        """
        resume the named node

        :param name: the name of the node
        :return: the dict of the node
        """
        raise NotImplementedError

    @abstractmethod
    def destroy(self, name=None):
        """
        Destroys the node
        :param name: the name of the node
        :return: the dict of the node
        """
        raise NotImplementedError

    @abstractmethod
    def create(self, name=None, image=None, size=None, timeout=360, **kwargs):
        """
        creates a named node

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

    @abstractmethod
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
        :param name: The anme of the key
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
        Gest the flavor with a given name
        :param name: The name of the flavor
        :return: The dict of the flavor
        """
        raise NotImplementedError

    def reboot(self, name=None):
        """
        Reboot a list of nodes with the given names

        :param names: A list of node names
        :return:  A list of dict representing the nodes
        """
        raise NotImplementedError

    def attach_publicip(self, name=None):
        """
        adds a public ip to the named vm

        :param name: Name of the vm
        :return:
        """
        raise NotImplementedError

    def delete_public_ip(self, ip=None):
        """
        Deletes the ip address

        :param ip: the ip addess, if None than all will be deleted
        :return:
        """
        raise NotImplementedError

    def list_public_ips(self, available=False):
        """
        Lists the public ip addresses.
        :param available: if True only those that are not allocated will be
                          retunred.
        :return:
        """
        raise NotImplementedError

    def create_public_ip(self):
        """
        Creates a new public IP address to use
        :return: The ip address information
        """

    def find_available_public_ip(self):
        """
        Returns a single public available ip address.
        :return: The ip
        """
