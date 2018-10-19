import abc


class CloudManagerABC(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass

    @abc.abstractmethod
    def info(self):
        pass

    @abc.abstractmethod
    def delete(self):
        pass

    @abc.abstractmethod
    def suspend(self):
        pass


    @abc.abstractmethod
    def ls(self):
        pass
