import abc


class DBProviderABC(metaclass=abc.ABCMeta):
    """
    Abstract Base Class for supported database providers.
    """

    @abc.abstractmethod
    def list_files(self):
        """
        get a list of stored files

        :return: a list of CloudFiles
        """
        pass

    @abc.abstractmethod
    def add(self, cloud_file):
        """
        add a new CloudFile to the database

        :param cloud_file: a CloudFile. todo
        :return: a CloudFile with resource information filled in
        """
        pass

    @abc.abstractmethod
    def delete(self, cloud_file):
        """
        delete a file from the database

        :param cloud_file: the cloud file entry being deleted
        """
        pass

    @abc.abstractmethod
    def update(self, cloud_file):
        """
        update a file

        :param cloud_file: the cloud file entry being updated
        :return: the updated CloudFile
        """
        pass
