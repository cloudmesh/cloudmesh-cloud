

class WindowsService(object):

    @staticmethod
    def delete(name="MongoDB"):
        """
        deletes the named service

        :param name:
        :return:
        """
        # use sd delete as posted in piazza
        # needs the service to be stopped we guess
        raise NotImplementedError

    @staticmethod
    def status(name="MongoDB"):
        """
        returns the status of the named service

        :param name:
        :return:
        """
        # use the sc query and status command as postedin piazz
        raise NotImplementedError

    @staticmethod
    def stop(name="MongoDB"):
        """
        sops the named service

        :param name:
        :return:
        """
        # use the stop command before you delete it
        raise NotImplementedError

    @staticmethod
    def uninstall(name=None):
        """
        uninstalls the named package. The name should be the msi
        :param name:
        :return:
        """
        # we do not know ho to do this from the commadline
        raise NotImplementedError


