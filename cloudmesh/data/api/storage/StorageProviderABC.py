import abc


class StorageProviderABC(metaclass=abc.ABCMeta):
    """
    Abstract Base Class for supported cloud providers.
    """

    @abc.abstractmethod
    def get(self, source, destination):
        """
        get a file stored with this provider

        :param source: the cloud file entry being retrieved
        :param destination: download destination
        :return: the downloaded cloud file binary
        """
        pass

    @abc.abstractmethod
    def put(self, source):
        """
        upload a file

        :param source: a CloudFile. todo
        :return: a CloudFile with resource information filled in
        """
        pass

    @abc.abstractmethod
    def delete(self, name):
        """
        delete a file from the provider

        :param name: the cloud file entry being deleted
        """
        pass

    @abc.abstractmethod
    def exists(self, name):
        """
        if a file exists in the remote storage provider

        :param name: a file name to check
        """
        pass
