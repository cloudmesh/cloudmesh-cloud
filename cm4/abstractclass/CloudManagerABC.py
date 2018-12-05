import abc


class CloudManagerABC(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def start(self, node_id):
        """
        start node
        """
        pass

    @abc.abstractmethod
    def stop(self, node_id):
        """
        stop node
        """
        pass

    @abc.abstractmethod
    def info(self, node_id):
        """
        get all information about one node
        """
        pass

    @abc.abstractmethod
    def suspend(self, node_id):
        """
        suspend one node
        """
        pass

    @abc.abstractmethod
    def ls(self):
        """
        list all nodes id
        """
        pass

    @abc.abstractmethod
    def resume(self, node_id):
        """
        resume one node
        """
        pass

    @abc.abstractmethod
    def destroy(self, node_id):
        """
        delete one node
        """
        pass

    @abc.abstractmethod
    def create(self, name, image=None, size=None, timeout=300, **kwargs):
        """
        create one node
        """
        pass

    def rename(self, name, new_name):
        """
        renames the node
        """
        pass

