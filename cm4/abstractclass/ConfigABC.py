import abc


class ResourceManagerABC(metaclass=abc.ABCMeta):

    # please update the abstract class
    # this abstract class used for yaml file

    @abc.abstractmethod
    def get(self):
        pass

    @abc.abstractmethod
    def set(self):
        pass
