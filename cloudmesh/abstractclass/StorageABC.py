from abc import ABCMeta, abstractmethod


# noinspection PyUnusedLocal
class StorageABC(metaclass=ABCMeta):

    def __init__(self, cloud, config):
        raise NotImplementedError

    def create_dir(service=None, directory=directorty):
        raise NotImplementedError

    def list(service=None, source=None, recursive=False):
        raise NotImplementedError

    def put(service=None, source=None, destination=None, recusrive=False):
        raise NotImplementedError

    def get(service=None, source=None, destination=None, recusrive=False):
        raise NotImplementedError

    def delete(service=None, source=None, recusrive=False):
        raise NotImplementedError

    def search(service=None, directory=None, filename=None, recusrive=False):
        raise NotImplementedError
