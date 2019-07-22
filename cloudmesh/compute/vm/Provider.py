from pprint import pprint

from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.common.Printer import Printer
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.console import Console
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.variables import Variables
from cloudmesh.management.configuration.config import Config
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
from cloudmesh.provider import Provider as ProviderList


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

        providers = ProviderList()

        if self.kind in ['openstack', 'azure', 'docker', "aws"]:
            provider = providers[self.kind]
        elif self.kind in ["awslibcloud", "google"]:
            from cloudmesh.compute.libcloud.Provider import \
                Provider as LibCloudProvider
            provider = LibCloudProvider
        elif self.kind in ["vagrant", "virtualbox"]:
            from cloudmesh.compute.virtualbox.Provider import \
                Provider as VirtualboxCloudProvider
            provider = VirtualboxCloudProvider
        elif self.kind in ["azureaz"]:
            from cloudmesh.compute.azure.AzProvider import \
                Provider as AzAzureProvider
            provider = AzAzureProvider

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

    def loop_n(self, func, **kwargs):

        try:
            names = Parameter.expand(kwargs['name'])
        except:
            ValueError("The name parameter is missing")

        r = []
        for name in names:
            parameters = dict(kwargs)
            parameters['name'] = name
            vm = func(**parameters)
            if type(vm) == list:
                r = r + vm
            elif type(vm) == dict:
                r.append(vm)
            else:
                raise NotImplementedError
        return r

    @DatabaseUpdate()
    def destroy(self, name=None):
        parameter = {'name': name}
        r = self.loop_n(self.p.destroy, **parameter)
        return r

    def loop(self, names, func, **kwargs):
        names = self.expand(names)
        r = []
        for name in names:
            vm = func(name, kwargs)
            r.append(vm)
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

    def find_clouds(self, names=None):
        names = self.expand(names)
        # not yet implemented

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

    def create(self,
               names=None,
               image=None,
               size=None,
               timeout=360,
               group=None,
               metadata=None,
               **kwargs):

        def upload_meta(cm):
            data = {'cm': str(cm)}
            pprint(data)
            self.set_server_metadata(name, **data)

        cm = CmDatabase()

        names = self.expand(names)
        r = []
        for name in names:
            StopWatch.start(f"create vm {name}")

            cm = {
                'kind': "vm",
                'name': name,
                'group': group,
                'cloud': self.cloudname(),
                'status': 'booting'
            }
            entry = {}
            entry.update(cm)

            result = self.cm.update(entry)

            data = self.p.create(
                name=name,
                image=image,
                size=size,
                timeout=360,
                group=group,
                metadata=metadata,
                **kwargs)

            StopWatch.stop(f"create vm {name}")
            t = format(StopWatch.get(f"create vm {name}"), '.2f')
            cm['creation_time'] = t

            entry.update(data)
            entry[metadata] = cm
            if metadata:
                entry.update(metadata)

            cm['status'] = 'available'
            upload_meta(cm)

            result = self.cm.update(entry)

            r.append(entry)
        return r

    def set_server_metadata(self, name, **metadata):
        """
        sets the metadata for the server

        :param name: name of the fm
        :param metadata: the metadata
        :return:
        """
        self.p.set_server_metadata(name, metadata)

    def get_server_metadata(self, name):
        """
        gets the metadata for the server

        :param name: name of the fm
        :return:
        """
        r = self.p.get_server_metadata(name)
        return r

    def delete_server_metadata(self, name, key):
        """
        gets the metadata for the server

        :param name: name of the fm
        :return:
        """
        r = self.p.delete_server_metadata(name, key)
        return r

    def rename(self, source=None, destination=None):
        self.p.rename(source=source, destination=destination)

    def key_upload(self, key):
        self.p.key_upload(key)

    def key_delete(self, key):
        self.p.key_delete(key)

    def name_parameter(self, name):
        if name is None:
            ValueError("Names is None")
        parameters = {
            'name': name
        }
        return parameters

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

    def remove_secgroup(self, name=None):
        return self.p.remove_secgroup(name=name)

    def add_secgroup(self, name=None):
        return self.p.add_secgroup(name=name)

    def upload_secgroup(self, name=None):
        return self.p.upload_secgroup(name=name)

    def delete_public_ip(self, ip):
        return self.p.delete_public_ip(ip)

    def list_public_ips(self, available=False):
        return self.p.list_public_ips(available=available)

    def create_public_ip(self):
        return self.p.create_public_ip()

    def find_available_public_ip(self):
        return self.p.find_available_public_ip()

    def detach_public_ip(self, name=None, ip=None):
        return self.p.detach_public_ip(name=name, ip=ip)

    def attach_public_ip(self, name=None, ip=None):
        return self.p.attach_public_ip(name=name, ip=ip)

    def get_public_ip(self, name=None):
        return self.p.get_public_ip(name=name)

    def ssh(self, vm=None, command=None):
        return self.p.ssh(vm=vm, command=command)
