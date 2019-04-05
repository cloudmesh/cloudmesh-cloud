from cloudmesh.compute.libcloud.Provider import Provider as LibCloudProvider
from cloudmesh.compute.docker.Provider import Provider as DockerProvider
from cloudmesh.compute.virtualbox.Provider import \
    Provider as VirtualboxCloudProvider
from cloudmesh.management.configuration.config import Config
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
from cloudmesh.common.console import Console

class Provider(object):

    def __init__(self, name=None,
                 configuration="~/.cloudmesh/.cloudmesh4.yaml"):
        try:
            self.kind = Config(configuration)["cloudmesh"]["cloud"][name]["cm"][
                "kind"]
            self.name = name
        except:
            Console.error(f"proider {name} not found in {configuration}")
            raise ValueError(f"proider {name} not found in {configuration}")

        provider = None

        if self.kind in ["openstack", "aws", "google"]:
            provider = LibCloudProvider
        elif self.kind in ["vagrant", "virtualbox"]:
            provider = VirtualboxCloudProvider
        elif self.kind in ["docker"]:
            provider = DockerProvider

        if provider is None:
            Console.error(f"proider {name} not supported")
            raise ValueError(f"proider {name} not supported")

        self.p = provider(name=name, configuration=configuration)


    def cloudname(self):
        return self.name

    @DatabaseUpdate()
    def keys(self):
        return self.p.keys()

    @DatabaseUpdate()
    def list(self):
        return self.p.list()

    @DatabaseUpdate()
    def images(self):
        return self.p.images()

    @DatabaseUpdate()
    def flavor(self):
        return self.p.flavors()

    def add_collection(self, d, *args):
        if d is None:
            return None
        label = '-'.join(args)
        for entry in d:
            entry['collection'] = label
        return d

    @DatabaseUpdate()
    def images(self):
        return self.p.images()

    # name
    # cloud
    # kind
    @DatabaseUpdate()
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

    def reboot(self, name=None):
        return self.p.reboot(name=name)

    def create(self, name=None, image=None, size=None, timeout=360, **kwargs):
        self.p.create(
            name=name,
            image=image,
            size=size,
            timeout=360,
            **kwargs)

    def rename(self, source=None, destination=None):
        self.p.rename(source=source, destination=destination)


    def key_upload(self, key):
        self.p.key_upload(key)