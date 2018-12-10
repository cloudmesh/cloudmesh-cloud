import abc


#
# if name is none, take last name from mongo, apply to last started vm
#


class CloudManagerABC(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def start(self, name):
        """
        start a node

        :param name: the unique node name
        :return:  The dict representing the node
        """
        pass

    @abc.abstractmethod
    def stop(self, name=None):
        """
        stops the node with the given name

        :param name:
        :return: The dict representing the node including updated status
        """
        pass

    @abc.abstractmethod
    def info(self, name=None):
        """
        gets the information of a node with a given name

        :param name:
        :return: The dict representing the node including updated status
        """
        pass

    @abc.abstractmethod
    def suspend(self, name=None):
        """
        suspends the node with the given name

        :param name: the name of the node
        :return: The dict representing the node
        """
        pass

    # list is a reserved keyword so we switch from list to nodes
    @abc.abstractmethod
    def nodes(self):
        """
        list all nodes id

        :return: an array of dicts representing the nodes
        """
        pass

    @abc.abstractmethod
    def resume(self, name=None):
        """
        resume the named node

        :param name: the name of the node
        :return: the dict of the node
        """
        pass

    @abc.abstractmethod
    def destroy(self, name=None):
        """
        Destroys the node
        :param name: the name of the node
        :return: the dict of the node
        """
        pass

    @abc.abstractmethod
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
        pass

    def rename(self, name=None, destination=None):
        """
        rename a node

        :param name: the current name
        :param new_name: the new name
        :return: the dict with the new name
        """
        # if destination is None, increase the name counter and use the new name
        pass

