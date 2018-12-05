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
        """
        Starts the VM(s).
        :return: None.
        """
        pass

    @abc.abstractmethod
    def stop(self):
        """
        Stops the VM(s)
        :return: None.
        """
        pass

    @abc.abstractmethod
    def status(self):
        """
        Provides the status of the VM(s)
        :return: a list of vm statuses.
        """
        pass