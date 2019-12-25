from pprint import pprint

from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.common.Printer import Printer
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.console import Console
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.variables import Variables
from cloudmesh.configuration.Config import Config
from cloudmesh.management.configuration.name import Name
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
from cloudmesh.provider import Provider as ProviderList
from cloudmesh.common.debug import VERBOSE

from cloudmesh.mongo.CmDatabase import CmDatabase


class Provider(ComputeNodeABC):

    def __init__(self,
                 name=None,
                 configuration="~/.cloudmesh/cloudmesh.yaml"):
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

        if self.kind in [
#            'openstack',
             'azure',
             'docker',
             "aws",
             "azureaz",
             "virtualbox"]:

            provider = providers[self.kind]

        elif self.kind in ["awslibcloud", "google"]:

            from cloudmesh.compute.libcloud.Provider import \
                Provider as LibCloudProvider
            provider = LibCloudProvider

        elif self.kind in ['openstack']:
            from cloudmesh.openstack.compute.Provider import \
                Provider as OpenStackComputeProvider
            provider = OpenStackComputeProvider

        elif self.kind in ['oracle']:
            from cloudmesh.oracle.compute.Provider import \
                Provider as OracleComputeProvider
            provider = OracleComputeProvider

        # elif self.kind in ["vagrant", "virtualbox"]:
        #    from cloudmesh.compute.virtualbox.Provider import \
        #        Provider as VirtualboxCloudProvider
        #    provider = VirtualboxCloudProvider
        # elif self.kind in ["azureaz"]:
        #    from cloudmesh.compute.azure.AzProvider import \
        #        Provider as AzAzureProvider
        #    provider = AzAzureProvider

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

    @DatabaseUpdate()
    def destroy(self, name=None):
        # bug should determine provider from name
        r = self.loop_name(name, self.p.destroy)
        return r

    def loop_name(self, names, func):
        names = self.expand(names)
        r = []
        for name in names:
            vm = func(name=name)
            if type(vm) == list:
                r = r + vm
            elif type(vm) == dict:
                r.append(vm)
            elif vm is None:
                pass
            else:
                raise NotImplementedError
        return r

    def loop(self, func, **kwargs):
        names = self.expand(kwargs['name'])

        r = []
        for name in names:
            parameters = dict(kwargs)
            parameters['name'] = name
            vm = func(**parameters)
            if type(vm) == list:
                r = r + vm
            elif type(vm) == dict:
                r.append(vm)
            elif vm is None:
                pass
            else:
                raise NotImplementedError
        return r

    @DatabaseUpdate()
    def keys(self):
        return self.p.keys()

    @DatabaseUpdate()
    def list(self, **kwargs):
        return self.p.list(**kwargs)

    @DatabaseUpdate()
    def flavor(self, **kwargs):
        return self.p.flavors(**kwargs)

    @DatabaseUpdate()
    def flavors(self, **kwargs):
        return self.p.flavors(**kwargs)

    def add_collection(self, d, *args):
        if d is None:
            return None
        label = '-'.join(args)
        for entry in d:
            entry['collection'] = label
        return d

    @DatabaseUpdate()
    def images(self, *args, **kwargs):
        return self.p.images(*args, **kwargs)

    @DatabaseUpdate()
    def create(self, **kwargs):

        arguments = dotdict(kwargs)
        name = arguments.name
        cloud = arguments.cloud

        if name is None:
            name_generator = Name()
            vms = [str(name_generator)]
        else:
            vms = self.expand(name)

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

        duplicates = []
        for vm in vms:
            query = {"name": vm}
            duplicates += database.find(collection=f'{cloud}-node', query=query)
        database.close_client()

        if len(duplicates) > 0:
            print(Printer.flatwrite(duplicates,
                                    order=['cm.name', 'cm.cloud'],
                                    header=['Name', 'Cloud'],
                                    output='table'))
            raise Exception("these vms already exists")

        # Step 2. identify the image and flavor from kwargs and if they do
        # not exist read them for that cloud from the yaml file

        if arguments.image is None:
            arguments.image = self.find_attribute('image', [variables, defaults])

        if arguments.image is None:
            raise ValueError("image not specified")

        if arguments.group is None:
            arguments.group = self.find_attribute('group', [variables, defaults])

        if arguments.group is None:
            arguments.group = "default"

        if arguments.size is None:
            arguments.size = self.find_attribute('size', [variables, defaults])

        if arguments.size is None:
            raise ValueError("size not specified")

        # Step 3: use the create command to create the vms

        # created = self.loop(vms, self.p.create, **arguments)
        arguments['name'] = vms

        created = self.loop(self._create, **arguments)

        VERBOSE(created)

        self.list()

        return created

    def _create(self, **arguments):

        arguments = dotdict(arguments)

        r = []

        StopWatch.start(f"create vm {arguments.name}")

        cm = {
            'kind': "vm",
            'name': arguments.name,
            'group': arguments.group,
            'cloud': self.cloudname(),
            'status': 'booting'
        }
        entry = {}
        entry.update(cm=cm, name=arguments.name)

        result = CmDatabase.UPDATE(entry, progress=False)[0]

        data = {}
        dryrun = False
        if "dryrun" in arguments:
            dryrun = arguments.dryrun
            data = {"dryrun": True}
        else:
            arguments.timeout = 360
            data = self.p.create(**arguments)
        # print('entry')
        # pprint(entry)
        # print('data')
        pprint(data)
        entry.update(data)

        StopWatch.stop(f"create vm {arguments.name}")
        t = format(StopWatch.get(f"create vm {arguments.name}"), '.2f')
        cm['creation_time'] = t

        entry.update({'cm': cm})

        if arguments.metadata:
            entry.update({"metadata": arguments.metadata})
        else:
            entry.update({"metadata": str({"cm": cm,
                                           "image": arguments.image,
                                           "size": arguments.size})})

        cm['status'] = 'available'
        self.p.set_server_metadata(arguments.name, cm)

        result = CmDatabase.UPDATE(entry, progress=False)[0]

        return result

    def find_attribute(self, name, dicts):
        for d in dicts:
            if name in d:
                return d[name]
        return None

    def find_clouds(self, name=None):
        # BUG: needs to work on name and not provider
        names = self.expand(name)
        # not yet implemented

    @DatabaseUpdate()
    def stop(self, name=None, **kwargs):
        # BUG: needs to work on name and not provider
        return self.loop_name(name, self.p.stop)

    @DatabaseUpdate()
    def start(self, name=None, **kwargs):
        # BUG: needs to work on name and not provider
        return self.loop_name(name, self.p.start)

    # @DatabaseUpdate()
    def info(self, name=None):
        # BUG: needs to work on name and not provider
        return self.loop_name(name, self.p.info)

    @DatabaseUpdate()
    def resume(self, name=None):
        # BUG: needs to work on name and not provider
        return self.loop(name, self.p.resume)

    def status(self, name=None):
        r = self.info(name=name)

        status = []
        for entry in r:
            state = {'name': entry['name'],
                     'status:': entry['status'],
                     'cm.status': entry['cm']['status']}
            status.append(state)
        return status

    @DatabaseUpdate()
    def reboot(self, name=None):
        # BUG: needs to work on name and not provider
        return self.loop(name, self.p.reboot)

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
    def suspend(self, name=None):
        raise NotImplementedError

    # noinspection PyPep8Naming
    def Print(self, data, output='table', kind=None):

        if kind is None and len(data) > 0:
            kind = data[0]["cm"]["kind"]

        if output == "table":

            order = self.p.output[kind]['order']  # not pretty
            header = self.p.output[kind]['header']  # not pretty

            if 'humanize' in self.p.output[kind]:
                humanize = self.p.output[kind]['humanize']
            else:
                humanize = None

            print(Printer.flatwrite(data,
                                    sort_keys=["name"],
                                    order=order,
                                    header=header,
                                    output=output,
                                    humanize=humanize)
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
        # VERBOSE(vm)
        return self.p.ssh(vm=vm, command=command)

    def console(self, vm=None):
        return self.p.console(vm=vm)

    def wait(self, vm=None, interval=None, timeout=None):
        return self.p.wait(vm=vm, interval=interval, timeout=timeout)

    def log(self, vm=None):
        return self.p.log(vm=vm)

    def add_secgroup_rule(self,
                          name=None,  # group name
                          port=None,
                          protocol=None,
                          ip_range=None):
        return self.p.add_secgroup_rule(name=name, port=port, protocol=protocol,
                                        ip_range=ip_range)

    def add_rules_to_secgroup(self, name=None, rules=None):
        return self.p.add_rules_to_secgroup(secgroupname=name, newrules=rules)

    def destroy(self, name=None):
        return self.p.destroy(name=name)
