import abc


class CloudProviderABC(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self, config):
        """
        Initializer for the cloud provider class.
        :param config: the object containing the configurations.
        """
        pass

    @abc.abstractmethod
    def start(self):

        pass

    @abc.abstractmethod
    def stop(self):
        pass

    @abc.abstractmethod
    def status(self):
        pass