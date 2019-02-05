from abc import ABCMeta, abstractmethod
from pprint import pprint
from datetime import datetime



# noinspection PyUnusedLocal
class FlavorABC(metaclass=ABCMeta):

    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def get(self, name=None):
        pass

