import abc

class DBProviderABC(metaclass = abc.ABCMeta):
    """
    Abstract Base Class for supported database providers.
    """

    @abc.abstractmethod
    def list_files(self):
        '''
        get a list of stored files
        :return: a list of CloudFiles
        '''
        pass

    @abc.abstractmethod
    def add(self, cloudFile):
        '''
        add a new CloudFile to the database
        
        todo: not sure if this should take a cloud file entry or not. path, policies might be a better choice
        
        :param cloudFile: a CloudFile. todo
        :return: a CloudFile with resource information filled in
        '''
        pass

    @abc.abstractmethod
    def delete(self, cloudFile):
        '''
        delete a file from the database
        :param cloudFile: the cloud file entry being deleted
        '''
        pass

    @abc.abstractmethod
    def update(self, cloudFile):
        '''
        update a file
        :param cloudFile: the cloud file entry being updated
        :return: the updated CloudFile
        '''
        pass
