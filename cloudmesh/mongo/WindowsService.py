import os
from cloudmesh.common.Shell import Shell
from pprint import pprint
from cloudmesh.common.console import Console


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
        os.system(f"sc delete {name}")

    @staticmethod
    def status(name="MongoDB"):
        """
        returns the status of the named service

        :param name:
        :return:
        """
        # use the sc query and status command as postedin piazz
        services = WindowsService.list()
        if name in services:
            return services[name]["STATE"].lower()
        else:
            return None

    @staticmethod
    def stop(name="MongoDB"):
        """
        sops the named service

        :param name:
        :return:
        """
        # use the stop command before you delete it
        raise NotImplementedError
        # use the Shell.execute or run command to redirect the output and than find the stat in the output

    @staticmethod
    def list():
        """
        lists the names of the running services
        :return:
        """
        services = {}
        r = Shell.execute("sc", ["query"])
        r = r.replace("\r\n", "\n")
        entries = r.split("\n\n")
        for entry in entries:
            attributes = entry.splitlines()
            element = {}
            for line in attributes:
                if ":" in line:
                    name, value = line.split(":", 1)
                    name = name.strip()
                    value = value.strip()
                    if name == "STATE":
                        element[name] = value[3:]
                    else:
                        element[name] = value

            services[element["SERVICE_NAME"]] = element
        return services

    @staticmethod
    def uninstall(name=None):
        """
        uninstalls the named package. The name should be the msi
        :param name:
        :return:
        """
        # we do not know ho to do this from the commadline
        raise NotImplementedError


if __name__ == "__main__":

    pprint(WindowsService.list())
    status = WindowsService.status(name="MongoDB")
    print("Status MongoDB", status)
    if status is not None:
        WindowsService.delete(name="MongoDB")
        Console.ok("Deleting the MongoDB service")
    else:
        Console.ok("Could not find the MongoDB servise")

    print("check if MongoDB is no longer in the service list")

    status = WindowsService.status(name="MongoDB")
    print("Status MongoDB", status)
    if status is None:
        Console.ok("deleted")
    else:
        Console.error("MongoDB is in the status", status)
