import abc


class CloudManagerABC(metaclass=abc.ABCMeta):

    # please update the abstract class
    # this abstract class used for any cloud instance

    @abc.abstractmethod
    def start(self):
        """
        start node
        """
        pass

    @abc.abstractmethod
    def stop(self):
        """
        stop node
        """
        pass

    @abc.abstractmethod
    def info(self):
        """
        get all information about one node
        """
        pass

    @abc.abstractmethod
    def suspend(self):
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
    def resume(self):
        """
        resume one node
        """
        pass

    @abc.abstractmethod
    def destroy(self):
        """
        delete one node
        """
        pass

    @abc.abstractmethod
    def create(self):
        """
        create one node
        """
        pass
