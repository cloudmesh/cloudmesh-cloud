import abc


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
    def stop(self, name):
        """
        stops the node with the given name

        :param name:
        :return: The dict representing the node including updated status
        """
        pass

    @abc.abstractmethod
    def info(self, name):
        """
        gets the information of a node with a given name

        :param name:
        :return: The dict representing the node including updated status
        """
        pass

    @abc.abstractmethod
    def suspend(self, name):
        """
        suspends the node with the given name

        :param name: the name of the node
        :return: The dict representing the node
        """
        pass

    @abc.abstractmethod
    def ls(self):
        """
        list all nodes id

        :return: an array of dicts representing the nodes
        """
        pass

    @abc.abstractmethod
    def resume(self, name):
        """
        resume the named node

        :param name: the name of the node
        :return: the dict of the node
        """
        pass

    @abc.abstractmethod
    def destroy(self, name):
        """
        Destroys the node
        :param name: the name of the node
        :return: the dict of the node
        """
        pass

    @abc.abstractmethod
    def create(self, name, image=None, size=None, timeout=360, **kwargs):
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

    def rename(self, name, new_name):
        """
        rename a node

        :param name: the current name
        :param new_name: the new name
        :return: the dict with the new name
        """
        pass

