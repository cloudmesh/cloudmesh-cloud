from cloudmesh.compute.libcloud.Provider import Provider as LibCloudProvider
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.console import Console

class Provider(object):

    def __init__(self, name=None, configuration="~/.cloudmesh/.cloudmesh4.yaml"):
        kind = Config(configuration)["cloudmesh"]["cloud"][name]["cm"]["kind"]


        Console.msg("FOUND Kind", kind)

        if kind in ["openstack"]:

            self.p = LibCloudProvider(name=name, configuration=configuration)

            print (self.p)
            print (self.p.kind)


    def list(self):
        return self.p.list()

    def images(self):
        return self.p.images()

    def flavors(self):
        return self.p.flavors()

    def start(self, name=None):
        return self.p.start(name=name)

    def stop(self, name=None):
        return self.p.stop(name=name)

    def info(self, name=None):
        return self.p.info(name=name)

    def resume(self, name=None):
        return self.p.resume(name=name)

    def resume(self, name=None):
        return self.p.resume(name=name)

    def reboot(self, name=None):
        return self.p.reboot(name=name)

    def create(self, name=None, image=None, size=None, timeout=360, **kwargs):
        self.p.create(
            name=name,
            image=image,
            size=size,
            timeout=360,
            **kwargs)

    def rename(self, name=None, destination=None):
        self.p.rename(name=name, destination=name)