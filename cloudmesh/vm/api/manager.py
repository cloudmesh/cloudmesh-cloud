from cloudmesh.management.configuration.config import Config


class Manager(object):

    def __init__(self, name=None):
        print("init {name}".format(name=self.__class__.__name__))
        config = Config()
        kind = config["cloudmesh.cloud." + name]
        # if kind == "vm":
        #    self.provider = cloudmesh.compute.libcloud.Provider()

    def list(self, parameter):
        print("list", parameter)
