from pprint import pprint

from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.variables import Variables
from cloudmesh.compute.azure.AzProvider import Provider as AzAzureProvider
from cloudmesh.compute.azure.PyAzure import Provider as PyAzureProvider
from cloudmesh.compute.docker.Provider import Provider as DockerProvider
from cloudmesh.compute.libcloud.Provider import Provider as LibCloudProvider
from cloudmesh.compute.openstack.Provider import Provider as \
    OpenStackCloudProvider
from cloudmesh.compute.virtualbox.Provider import \
    Provider as VirtualboxCloudProvider
from cloudmesh.management.configuration.config import Config
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate


class Provider(ComputeNodeABC):

    def __init__(self,
                 name=None,
                 configuration="~/.cloudmesh/cloudmesh4.yaml"):
        # noinspection PyPep8
        try:
            super().__init__(name, configuration)
            self.kind = Config(configuration)[f"cloudmesh.cloud.{name}.cm.kind"]
            self.credentials = Config(configuration)[
                f"cloudmesh.cloud.{name}.credentials"]
            self.name = name
        except:
            Console.error(f"provider {name} not found in {configuration}")
            raise ValueError(f"provider {name} not found in {configuration}")

        provider = None

        if self.kind in ["openstack"]:
            provider = OpenStackCloudProvider
        elif self.kind in ["aws"]:
            provider = LibCloudProvider
        elif self.kind in ["google"]:
            provider = LibCloudProvider
        elif self.kind in ["vagrant", "virtualbox"]:
            provider = VirtualboxCloudProvider
        elif self.kind in ["docker"]:
            provider = DockerProvider
        elif self.kind in ["azure"]:
            provider = AzAzureProvider
        elif self.kind in ["pyazure"]:
            provider = PyAzureProvider

        if provider is None:
            Console.error(f"provider {name} not supported")
            raise ValueError(f"provider {name} not supported")

        self.p = provider(name=name, configuration=configuration)

    def cloudname(self):
        return self.name

    def expand(self, names):
        if type(names) == list:
            return names
        else:
            return Parameter.expand(names)

    def loop(self, names, func, **kwargs):
        names = self.expand(names)
        r = []
        for name in names:
            VERBOSE(name)
            VERBOSE(func)
            vm = func(name, kwargs)
            VERBOSE(vm)
            r.append(vm)
            VERBOSE(r)
        return r

    @DatabaseUpdate()
    def keys(self):
        return self.p.keys()

    @DatabaseUpdate()
    def list(self):
        return self.p.list()

    @DatabaseUpdate()
    def flavor(self):
        return self.p.flavors()

    @DatabaseUpdate()
    def flavors(self):
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

    @DatabaseUpdate()
    def start(self, names=None, cloud=None, **kwargs):

        #
        # this is used to resume a vm, after it was stopped
        #
        raise NotImplementedError

    @DatabaseUpdate()
    def create2(self, names=None, cloud=None, **kwargs):

        arguments = dotdict(kwargs)
        vms = self.expand(names)

        #
        # Step 0, find the cloud
        #
        variables = Variables()
        if cloud is None:
            arguments.cloud = cloud = variables['cloud']

        # Step 1. iterate through the names to see if they already exist in
        # the DB and fail if one of them already exists

        database = CmDatabase()
        defaults = Config()[f"cloudmesh.cloud.{cloud}.default"]
        pprint(defaults)
        duplicates = []
        for vm in vms:
            duplicates += database.find(collection=f'{cloud}-node', name=vm)

        if len(duplicates) > 0:
            print(Printer.flatwrite(duplicates,
                                    order=['name', 'cm.cloud', 'state',
                                           'image',
                                           'size',
                                           'public_ips', 'cm.created'],
                                    header=['Name', 'Cloud', 'State', 'Image',
                                            'Size',
                                            'Public ips', 'created'],
                                    output='table'))
            raise Exception("these vms already exists")
            return None

        # Step 2. identify the image and flavor from kwargs and if they do
        # not exist read them for that cloud from the yaml file

        arguments.image = self.find_attribute('image', [variables, defaults])
        pprint(arguments.image)
        if 'image' is None:
            raise ValueError("image not specified")

        arguments.flavor = self.find_attribute('flavor', [variables, defaults])
        pprint(arguments.flavor)
        if 'flavor' is None:
            raise ValueError("image not specified")

        # Step 3: use the create command to create the vms

        pprint(arguments)

        created = self.loop(names, self.p.create, **arguments)

        pprint(created)
        return created

    def find_attribute(self, name, dicts):
        for d in dicts:
            if name in d:
                return d[name]
        return None

    @DatabaseUpdate()
    def stop(self, names=None, **kwargs):
        return self.loop(names, self.p.stop, **kwargs)

    def info(self, name=None):
        return self.p.info(name=name)

    @DatabaseUpdate()
    def resume(self, names=None):
        return self.loop(names, self.p.resume)

    @DatabaseUpdate()
    def reboot(self, names=None):
        return self.loop(names, self.p.reboot)

    @DatabaseUpdate()
    def create(self, names=None, image=None, size=None, timeout=360, **kwargs):
        names = self.expand(names)
        r = []
        for name in names:
            entry = self.p.create(
                name=name,
                image=image,
                size=size,
                timeout=360,
                **kwargs)
            r.append(entry)
        return r

    def rename(self, source=None, destination=None):
        self.p.rename(source=source, destination=destination)

    def key_upload(self, key):
        self.p.key_upload(key)

    def key_delete(self, key):
        self.p.key_delete(key)

    @DatabaseUpdate()
    def destroy(self, names=None, **kwargs):
        # this should later check and remove destroyed nodes, not implemented
        return self.loop(names, self.p.destroy, **kwargs)

    def ssh(self, name, command):
        self.p.ssh(name=name, command=command)
        # for name, ips in name_ips.items():
        # self.p.ssh(name=name, ips=ips, **kwargs)

    def login(self):
        if self.kind != "azure":
            raise NotImplementedError
        else:
            self.p.login()

    @DatabaseUpdate()
    def suspend(self, names=None):
        raise NotImplementedError

    # noinspection PyPep8Naming
    def Print(self, output, kind, data):
        if output == "table":

            order = self.p.output[kind]['order']  # not pretty
            header = self.p.output[kind]['header']  # not pretty

            print(Printer.flatwrite(data,
                                    sort_keys=["name"],
                                    order=order,
                                    header=header,
                                    output=output)
                  )
        else:
            print(Printer.write(data, output=output))

    def list_secgroups(self):
        return self.p.list_secgroups()

    def list_secgroups_rules(self):
        return self.p.list_secgroup_rules()
