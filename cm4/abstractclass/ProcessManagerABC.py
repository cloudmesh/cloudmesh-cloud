import abc


class ProcessManagerABC(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def run_command(self):
        """
        run command in node
        """
        pass

    @abc.abstractmethod
    def run_script(self):
        """
        run script in node
        """
        pass

    @abc.abstractmethod
    def parallel(self):
        """
        run anything in nodes parallel
        """
        pass
