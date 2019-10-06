
import os

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
        os.system(f"sc delete {name}")


    @staticmethod
    def status(name="MongoDB"):
        """
        returns the status of the named service

        :param name:
        :return:
        """
        # use the sc query and status command as postedin piazz
        raise NotImplementedError
        os.system(f"sc delete {name}")


    @staticmethod
    def stop(name="MongoDB"):
        """
        sops the named service

        :param name:
        :return:
        """
        # use the stop command before you delete it
        raise NotImplementedError
        os.system(f'sc query {name} | findstr /i "STATE"')
        # use the Shell.execute or run command to redirect the output and than find the stat in the output

    @staticmethod
    def list():
        """
        lists the names of the running services
        :return:
        """
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


