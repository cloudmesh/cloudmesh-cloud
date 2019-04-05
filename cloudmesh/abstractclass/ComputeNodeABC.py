from abc import ABCMeta, abstractmethod


# noinspection PyUnusedLocal
class ComputeNodeABC(metaclass=ABCMeta):

    def __init__(self, cloud, config):
        self.cloud = cloud
        self.cm = config["cloud"][cloud]["cm"]
        self.default = config["cloud"][cloud]["default"]
        self.credentials = config["cloud"][cloud]["credentials"]
        self.group = config["default"]["group"]
        self.experiment = config["default"]["experiment"]

    '''
    def map_default(self, r):
        """
        Adds common properties to libcloud results.
        Transforms result from its original strongly typed
        form to `dict`.

        Child providers should still implement their own
        result mapper as well for cloud specific redaction.

        :param r:
        :return: a result as dict
        """
        if not isinstance(r, dict):
            r = r.__dict__

        r["cloud"] = self.cloud
        r["modified"] = str(datetime.utcnow())
        return r

    def map_vm_create(self, c):
        """
        Includes `group` and `experiment` fields in
        the result. Separate from `_map_default` because
        these fields should only be set when something is
        created and are unique to VM objects.
        """
        c = self.map_default(c)
        c["group"] = self.group
        c["experiment"] = self.experiment
        c["created_at"] = str(datetime.utcnow())
        c["state"] = "creating"
        return c

    def print_config(self):
        print("cm:")
        pprint(self.cm)
        print("default:")
        pprint(self.default)
        print("Credentials:")
        pprint(self.credentials)
    '''

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
        list all nodes id

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

