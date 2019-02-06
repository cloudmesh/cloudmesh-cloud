from abc import ABCMeta, abstractmethod


# noinspection PyUnusedLocal
class ImageABC(metaclass=ABCMeta):

    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def get(self, name=None):
        pass

