import abc


class DatabaseManagerABC (metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def update_document(self):
        """
        update document in database/storage
        """
        pass

    @abc.abstractmethod
    def find_document(self):
        """
        find document in database/stroage
        """
        pass

    @abc.abstractmethod
    def delete_document(self):
        """
        delete any document in database/storage
        """
        pass
