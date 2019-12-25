import os
import subprocess
from ast import literal_eval
from time import sleep
from sys import platform
import ctypes

import openstack
from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.common.variables import Variables
from cloudmesh.common.DictList import DictList
from cloudmesh.configuration.Config import Config
from cloudmesh.image.Image import Image
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.provider import ComputeProviderPlugin
from cloudmesh.secgroup.Secgroup import Secgroup, SecgroupRule
from cloudmesh.common.DateTime import DateTime
from cloudmesh.common.debug import VERBOSE
from cloudmesh.image.Image import Image


class Provider(ComputeNodeABC, ComputeProviderPlugin):
    kind = "openstack"

    sample = """
    cloudmesh:
      cloud:
        {name}:
          cm:
            active: true
            heading: {name}
            host: TBD
            label: {name}
            kind: openstack
            version: liberty
            service: compute
          credentials:
            OS_AUTH_URL: https://{uri}:5000/v2.0
            OS_USERNAME: TBD
            OS_PASSWORD: TBD
            OS_TENANT_NAME: {tenant}
            OS_TENANT_ID: {tenant}
            OS_PROJECT_NAME: {tenant}
            OS_PROJECT_DOMAIN_ID: default
            OS_USER_DOMAIN_ID: default
            OS_VERSION: kilo
            OS_REGION_NAME: {region}
            OS_KEY_PATH: ~/.ssh/id_rsa.pub
          default:
            size: m1.medium
            image: CC-Ubuntu18.04
            username: TBD
        """

    vm_state = [
        'ACTIVE',
        'BUILDING',
        'DELETED',
        'ERROR',
        'HARD_REBOOT',
        'PASSWORD',
        'PAUSED',
        'REBOOT',
        'REBUILD',
        'RESCUED',
        'RESIZED',
        'REVERT_RESIZE',
        'SHUTOFF',
        'SOFT_DELETED',
        'STOPPED',
        'SUSPENDED',
        'UNKNOWN',
        'VERIFY_RESIZE'
    ]

    output = {
        "status": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.cloud",
                      "vm_state",
                      "status",
                      "task_state"],
            "header": ["Name",
                       "Cloud",
                       "State",
                       "Status",
                       "Task"]
        },
        "vm": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.cloud",
                      "vm_state",
                      "status",
                      "task_state",
                      "metadata.image",
                      "metadata.flavor",
                      "ip_public",
                      "ip_private",
                      "project_id",
                      "cm.creation_time",
                      "launched_at",
                      "cm.kind"],
            "header": ["Name",
                       "Cloud",
                       "State",
                       "Status",
                       "Task",
                       "Image",
                       "Flavor",
                       "Public IPs",
                       "Private IPs",
                       "Project ID",
                       "Creation time",
                       "Started at",
                       "Kind"],
            "humanize": ["launched_at"]
        },
        "image": {
            "sort_keys": ["cm.name",
                          "extra.minDisk"],
            "order": ["cm.name",
                      "size",
                      "min_disk",
                      "min_ram",
                      "status",
                      "cm.driver"],
            "header": ["Name",
                       "Size (Bytes)",
                       "MinDisk (GB)",
                       "MinRam (MB)",
                       "Status",
                       "Driver"]
        },
        "flavor": {
            "sort_keys": ["cm.name",
                          "vcpus",
                          "disk"],
            "order": ["cm.name",
                      "vcpus",
                      "ram",
                      "disk"],
            "header": ["Name",
                       "VCPUS",
                       "RAM",
                       "Disk"]
        },
        "key": {
            "sort_keys": ["name"],
            "order": ["name",
                      "type",
                      "format",
                      "fingerprint",
                      "comment"],
            "header": ["Name",
                       "Type",
                       "Format",
                       "Fingerprint",
                       "Comment"]
        },
        "secrule": {
            "sort_keys": ["name"],
            "order": ["name",
                      "tags",
                      "direction",
                      "ethertype",
                      "port_range_max",
                      "port_range_min",
                      "protocol",
                      "remote_ip_prefix",
                      "remote_group_id"
                      ],
            "header": ["Name",
                       "Tags",
                       "Direction",
                       "Ethertype",
                       "Port range max",
                       "Port range min",
                       "Protocol",
                       "Range",
                       "Remote group id"]
        },
        "secgroup": {
            "sort_keys": ["name"],
            "order": ["name",
                      "tags",
                      "description",
                      "rules"
                      ],
            "header": ["Name",
                       "Tags",
                       "Description",
                       "Rules"]
        },
        "ip": {
            "order": ["name", 'floating_ip_address', 'fixed_ip_address'],
            "header": ["Name", 'Floating', 'Fixed']
        },
    }

    # noinspection PyPep8Naming
    def Print(self, data, output=None, kind=None):

        if output == "table":
            if kind == "secrule":
                # this is just a temporary fix, both in sec.py and here the secgruops and secrules should be separated
                result = []
                for group in data:
                    # for rule in group['security_group_rules']:
                    #     rule['name'] = group['name']
                    result.append(group)
                data = result

            order = self.output[kind]['order']  # not pretty
            header = self.output[kind]['header']  # not pretty
            # humanize = self.output[kind]['humanize']  # not pretty

            print(Printer.flatwrite(data,
                                    sort_keys=["name"],
                                    order=order,
                                    header=header,
                                    output=output,
                                    # humanize=humanize
                                    )
                  )
        else:
            print(Printer.write(data, output=output))

    @staticmethod
    def _get_credentials(config):
        """
        Internal function to create a dict for the openstacksdk credentials.

        :param config: The credentials from the cloudmesh yaml file
        :return: the dict for the openstacksdk
        """

        d = {'version': '2', 'username': config['OS_USERNAME'],
             'password': config['OS_PASSWORD'],
             'auth_url': config['OS_AUTH_URL'],

             'region_name': config['OS_REGION_NAME'],
             }
        if 'OS_TENANT_ID' in config:
            d['tenant_id'] = config['OS_TENANT_ID']
        if 'OS_TENANT_NAME' in config:
            d['project_id'] = config['OS_TENANT_NAME']
        # d['project_domain_name'] = config['OS_PROJECT_NAME']
        return d

    def __init__(self, name=None, configuration="~/.cloudmesh/cloudmesh.yaml"):
        """
        Initializes the provider. The default parameters are read from the
        configuration file that is defined in yaml format.

        :param name: The name of the provider as defined in the yaml file
        :param configuration: The location of the yaml configuration file
        """

        conf = Config(configuration)["cloudmesh"]
        super().__init__(name, conf)

        self.user = Config()["cloudmesh"]["profile"]["user"]
        self.spec = conf["cloud"][name]
        self.cloud = name

        self.default = self.spec["default"]
        self.cloudtype = self.spec["cm"]["kind"]

        self.cred = self.spec["credentials"]
        if self.cred["OS_PASSWORD"] == 'TBD':
            Console.error(f"The password TBD is not allowed in cloud {name}")
        self.credential = self._get_credentials(self.cred)

        self.cloudman = openstack.connect(**self.credential)

        # self.default_image = deft["image"]
        # self.default_size = deft["size"]
        # self.default.location = cred["datacenter"]

        try:
            self.public_key_path = conf["profile"]["publickey"]
            self.key_path = path_expand(
                Config()["cloudmesh"]["profile"]["publickey"])
            f = open(self.key_path, 'r')
            self.key_val = f.read()
        except:
            raise ValueError("the public key location is not set in the "
                             "profile of the yaml file.")

    def update_dict(self, elements, kind=None):
        """
        THis function adds a cloudmesh cm dict to each dict in the list
        elements.
        Libcloud
        returns an object or list of objects With the dict method
        this object is converted to a dict. Typically this method is used
        internally.

        :param elements: the list of original dicts. If elements is a single
                         dict a list with a single element is returned.
        :param kind: for some kinds special attributes are added. This includes
                     key, vm, image, flavor.
        :return: The list with the modified dicts
        """

        if elements is None:
            return None
        elif type(elements) == list:
            _elements = elements
        else:
            _elements = [elements]
        d = []
        for entry in _elements:

            if "cm" not in entry:
                entry['cm'] = {}

            if kind == 'ip':
                entry['name'] = entry['floating_ip_address']

            entry["cm"].update({
                "kind": kind,
                "driver": self.cloudtype,
                "cloud": self.cloud,
                "name": entry['name']
            })

            if kind == 'key':

                try:
                    entry['comment'] = entry['public_key'].split(" ", 2)[2]
                except:
                    entry['comment'] = ""
                entry['format'] = \
                    entry['public_key'].split(" ", 1)[0].replace("ssh-", "")

            elif kind == 'vm':

                entry["cm"]["updated"] = str(DateTime.now())
                if "created_at" in entry:
                    entry["cm"]["created"] = str(entry["created_at"])
                    # del entry["created_at"]
                    if 'status' in entry:
                        entry["cm"]["status"] = str(entry["status"])
                else:
                    entry["cm"]["created"] = entry["modified"]

            elif kind == 'flavor':

                entry["cm"]["created"] = entry["updated"] = str(
                    DateTime.now())

            elif kind == 'image':

                entry["cm"]["created"] = entry["updated"] = str(
                    DateTime.now())

            # elif kind == 'secgroup':
            #    pass

            d.append(entry)
        return d

    def find(self, elements, name=None):
        """
        Finds an element in elements with the specified name.

        :param elements: The elements
        :param name: The name to be found
        :return:
        """

        for element in elements:
            if element["name"] == name or element["cm"]["name"] == name:
                return element
        return None

    def keys(self):
        """
        Lists the keys on the cloud

        :return: dict
        """
        return self.get_list(self.cloudman.list_keypairs(),
                             kind="key")

    def key_upload(self, key=None):
        """
        uploads the key specified in the yaml configuration to the cloud
        :param key:
        :return:
        """

        name = key["name"]
        cloud = self.cloud
        Console.msg(f"upload the key: {name} -> {cloud}")
        try:
            r = self.cloudman.create_keypair(name, key['public_key'])
        except:  # openstack.exceptions.ConflictException:
            raise ValueError(f"key already exists: {name}")

        return r

    def key_delete(self, name=None):
        """
        deletes the key with the given name
        :param name: The name of the key
        :return:
        """

        cloud = self.cloud
        Console.msg(f"delete the key: {name} -> {cloud}")
        r = self.cloudman.delete_keypair(name)

        return r

    def list_secgroups(self, name=None):
        """
        List the named security group

        :param name: The name of the group, if None all will be returned
        :return:
        """
        groups = self.cloudman.network.security_groups()

        if name is not None:
            for entry in groups:

                if entry['name'] == name:
                    groups = [entry]
                    break

        return self.get_list(
            groups,
            kind="secgroup")

    def list_secgroup_rules(self, name='default'):
        """
        List the named security group

        :param name: The name of the group, if None all will be returned
        :return:
        """
        return self.list_secgroups(name=name)

    def add_secgroup(self, name=None, description=None):
        """
        Adds the
        :param name: Name of the group
        :param description: The description
        :return:
        """
        if self.cloudman:
            if description is None:
                description = name
            try:
                self.cloudman.create_security_group(name,
                                                    description)
            except:
                Console.warning(f"secgroup {name} already exists in cloud. "
                                f"skipping.")
        else:
            raise ValueError("cloud not initialized")

    def add_secgroup_rule(self,
                          name=None,  # group name
                          port=None,
                          protocol=None,
                          ip_range=None):
        """
        Adds the
        :param name: Name of the group
        :param description: The description
        :return:
        """
        if self.cloudman:
            try:
                portmin, portmax = port.split(":")
            except:
                portmin = None
                portmax = None

            self.cloudman.create_security_group_rule(
                name,
                port_range_min=portmin,
                port_range_max=portmax,
                protocol=protocol,
                remote_ip_prefix=ip_range,
                remote_group_id=None,
                direction='ingress',
                ethertype='IPv4',
                project_id=None)

        else:
            raise ValueError("cloud not initialized")

    def remove_secgroup(self, name=None):
        """
        Delete the names security group

        :param name: The name
        :return:
        """
        if self.cloudman:
            self.cloudman.delete_security_group(name)
            g = self.list_secgroups(name=name)
            return len(g) == 0
        else:
            raise ValueError("cloud not initialized")

    def upload_secgroup(self, name=None):

        cgroups = self.list_secgroups(name)
        group_exists = False
        if len(cgroups) > 0:
            print("Warning group already exists")
            group_exists = True

        groups = Secgroup().list()
        rules = SecgroupRule().list()

        # pprint (rules)
        data = {}
        for rule in rules:
            data[rule['name']] = rule

        # pprint (groups)

        for group in groups:
            if group['name'] == name:
                break
        print("upload group:", name)

        if not group_exists:
            self.add_secgroup(name=name, description=group['description'])

            for r in group['rules']:
                if r != 'nothing':
                    found = data[r]
                    print("    ", "rule:", found['name'])
                    self.add_secgroup_rule(
                        name=name,
                        port=found["ports"],
                        protocol=found["protocol"],
                        ip_range=found["ip_range"])

        else:

            for r in group['rules']:
                if r != 'nothing':
                    found = data[r]
                    print("    ", "rule:", found['name'])
                    self.add_rules_to_secgroup(
                        name=name,
                        rules=[found['name']])

    # ok
    def add_rules_to_secgroup(self, name=None, rules=None):
        if name is None and rules is None:
            raise ValueError("name or rules are None")

        cgroups = self.list_secgroups(name)
        if len(cgroups) == 0:
            raise ValueError("group does not exist")

        groups = DictList(Secgroup().list())
        rules_details = DictList(SecgroupRule().list())

        try:
            group = groups[name]
        except:
            raise ValueError("group does not exist")

        for rule in rules:
            try:
                found = rules_details[rule]
                self.add_secgroup_rule(name=name,
                                       port=found["ports"],
                                       protocol=found["protocol"],
                                       ip_range=found["ip_range"])
            except:
                ValueError("rule can not be found")

    # not tested
    def remove_rules_from_secgroup(self, name=None, rules=None):

        if name is None and rules is None:
            raise ValueError("name or rules are None")

        cgroups = self.list_secgroups(name)
        if len(cgroups) == 0:
            raise ValueError("group does not exist")

        groups = DictList(Secgroup().list())
        rules_details = DictList(SecgroupRule().list())

        try:
            group = groups[name]
        except:
            raise ValueError("group does not exist")

        for rule in rules:
            try:
                found = rules_details[rule]
                try:
                    pmin, pmax = rules['ports'].split(":")
                except:
                    pmin = None
                    pmax = None
            except:
                ValueError("rule can not be found")

            for r in cgroups['security_group_rules']:

                test = \
                    r["port_range_max"] == pmin and \
                    r["port_range_min"] == pmax and \
                    r["protocol"] == found["protocol"] and \
                    r["remote_ip_prefix"] == found["ports"]
                # r["direction"] == "egress" \
                # r["ethertype"] == "IPv6" \
                # r["id"] == "1234e4e3-ba72-4e33-9844-..." \
                # r["remote_group_id"]] == null \
                # r["tenant_id"]] == "CH-12345"

                if test:
                    id = r["security_group_id"]
                    self.cloudman.delete_security_group_rule(id)

    def get_list(self, d, kind=None, debug=False, **kwargs):
        """
        Lists the dict d on the cloud
        :return: dict or libcloud object
        """

        if self.cloudman:
            entries = []
            for entry in d:
                entries.append(dict(entry))
            # VERBOSE(entries)

            return self.update_dict(entries, kind=kind)
        return None

    def images(self, **kwargs):
        """
        Lists the images on the cloud
        :return: dict or libcloud object
        """
        return self.get_list(self.cloudman.compute.images(),
                             kind="image")

    def image(self, name=None):
        """
        Gets the image with a given name
        :param name: The name of the image
        :return: the dict of the image
        """
        return self.find(self.images(), name=name)

    def flavors(self, **kwargs):
        """
        Lists the flavors on the cloud

        :return: dict of flavors
        """
        if kwargs is None:
            result = self.get_list(self.cloudman.compute.flavors(),
                                   kind="flavor")
        if "name" in kwargs:
            result = self.flavor(name=kwargs['name'])

        else:
            result = self.get_list(self.cloudman.compute.flavors(**kwargs),
                                   kind="flavor")

        return result

    def flavor(self, name=None):
        """
        Gets the flavor with a given name
        :param name: The name of the flavor
        :return: The dict of the flavor
        """
        return self.find(self.flavors(), name=name)

    def start(self, name=None):
        """
        Start a server with the given name

        :param name: A list of node name
        :return:  A list of dict representing the nodes
        """
        server = self.cloudman.get_server(name)['id']
        r = self.cloudman.compute.start_server(server)
        return r

    def stop(self, name=None):
        """
        Stop a list of nodes with the given name

        :param name: A list of node name
        :return:  A list of dict representing the nodes
        """
        server = self.cloudman.get_server(name)['id']
        r = self.cloudman.compute.stop_server(server)
        return r

    def pause(self, name=None):
        """
        Start a server with the given name

        :param name: A list of node name
        :return:  A list of dict representing the nodes
        """
        server = self.cloudman.get_server(name)['id']
        r = self.cloudman.compute.pause_server(server)

        return r

    def unpause(self, name=None):
        """
        Stop a list of nodes with the given name

        :param name: A list of node name
        :return:  A list of dict representing the nodes
        """
        server = self.cloudman.get_server(name)['id']
        r = self.cloudman.compute.unpause_server(server)

        return r

    def info(self, name=None):
        """
        Gets the information of a node with a given name

        :param name: The name of teh virtual machine
        :return: The dict representing the node including updated status
        """
        data = self.cloudman.list_servers(filters={'name': name})

        """
        vms = self.list()
        print ("VMS", vms)
        data = None
        for entry in vms:
            print ("FFF", entry['name'])
            if entry['name'] == name:
                data = entry
                break
        """

        if data is None:
            raise ValueError(f"vm not found {name}")

        r = self.update_dict(data, kind="vm")
        return r

    def status(self, name=None):

        r = self.cloudman.list_servers(filters={'name': name})[0]
        return r['status']

    def suspend(self, name=None):
        """
        NOT YET IMPLEMENTED.

        suspends the node with the given name.

        :param name: the name of the node
        :return: The dict representing the node
        """
        # UNTESTED
        server = self.cloudman.get_server(name)['id']
        r = self.cloudman.compute.suspend_server(server)

        return r

        """
        raise NotImplementedError

        #
        # BUG THIS CODE DOES NOT WORK
        #
        nodes = self.list()
        for node in nodes:
            if node.name == name:
                r = self.cloudman.ex_stop_node(self._get_node(node.name),
                                               deallocate=False)
                # print(r)
                # BUG THIS IS NOT A DICT
                return(node, name=name)
                self.cloudman.destroy_node(node)

        #
        # should return the updated names dict, e.g. status and so on
        # the above specification is for one name
        #
        
        return None
        """

    def resume(self, name=None):
        """
        resume a stopped node.

        :param name: the name of the node
        :return: the dict of the node
        """
        server = self.cloudman.get_server(name)['id']
        r = self.cloudman.compute.resume_server(server)

        return r

    def list(self):
        """
        Lists the vms on the cloud

        :return: dict of vms
        """
        servers = self.get_list(self.cloudman.compute.servers(), kind="vm")

        result = []
        for server in servers:

            if 'cm' in server['metadata']:
                metadata = server['metadata']['cm']
                cm = literal_eval(metadata)
                if 'cm' in server:
                    server['cm'].update(cm)
            try:
                server['ip_public'] = self.get_public_ip(server=server)
            except:
                pass
            try:
                server['ip_private'] = self.get_private_ip(server=server)
            except:
                pass
            result.append(server)

        return result

    def destroy(self, name=None):
        """
        Destroys the node
        :param name: the name of the node
        :return: the dict of the node
        """
        server = self.info(name=name)[0]
        r = self.cloudman.delete_server(name)
        server['status'] = 'DELETED'

        servers = self.update_dict([server], kind='vm')
        return servers

    def reboot(self, name=None):
        """
        Reboot a list of nodes with the given name

        :param name: A list of node name
        :return:  A list of dict representing the nodes
        """
        server = self.cloudman.get_server(name)['id']
        r = self.cloudman.compute.reboot_server(server)

        return r

    def set_server_metadata(self, name, cm):
        """
        Sets the server metadata from the cm dict

        :param name: The name of the vm
        :param cm: The cm dict
        :return:
        """
        data = {'cm': str(cm)}
        server = self.cloudman.get_server(name)
        self.cloudman.set_server_metadata(server, data)

    def get_server_metadata(self, name):
        server = self.info(name=name)
        m = self.cloudman.get_server_meta(server)
        data = dict(m['server_vars']['metadata'])
        return data

    def delete_server_metadata(self, name, key):
        server = self.info(name=name)
        m = self.cloudman.delete_server_metadata(server, key)
        m = self.cloudman.get_server_meta(server)
        data = dict(m['server_vars']['metadata'])
        return data

    def create(self,
               name=None,
               image=None,
               size=None,
               location=None,
               timeout=360,
               key=None,
               secgroup=None,
               ip=None,
               user=None,
               public=True,
               group=None,
               metadata=None,
               cloud=None,
               **kwargs):
        """
        creates a named node


        :param group: the list of groups the vm belongs to
        :param name: the name of the node
        :param image: the image used
        :param size: the size of the image
        :param timeout: a timeout in seconds that is invoked in case the image
                        does not boot. The default is set to 3 minutes.
        :param kwargs: additional arguments HEADING(c=".")ed along at time of
                       boot
        :return:
        """
        image_use = None
        flavor_use = None

        # keyname = Config()["cloudmesh"]["profile"]["user"]
        # ex_keyname has to be the registered keypair name in cloud

        """
        https://docs.openstack.org/openstacksdk/latest/user/connection.html#openstack.connection.Connection.create_server

        """

        if 'flavor' in kwargs and size is None:
            size = kwargs['flavor']

        # Guess user name

        if user is None:
            user = Image.guess_username(image)
            # image_name = image.lower()
            # if image_name.startswith("cc-"):
            #    user = "cc"
            # if "centos" in image_name:
            #    user = "centos"
            # elif "ubuntu" in image_name:
            #    user = "ubuntu"

        # get IP

        if not ip and public:
            ip = self.find_available_public_ip()
            # pprint(entry)

        elif ip is not None:
            entry = self.list_public_ips(ip=ip, available=True)
            if len(entry) == 0:
                print("ip not available")
                raise ValueError(f"The ip can not be assigned {ip}")

        if type(group) == str:
            groups = Parameter.expand(group)

        banner("Create Server")
        Console.msg(f"    Name:     {name}")
        Console.msg(f"    User:     {user}")
        Console.msg(f"    IP:       {ip}")
        Console.msg(f"    Image:    {image}")
        Console.msg(f"    Size:     {size}")
        Console.msg(f"    Public:   {public}")
        Console.msg(f"    Key:      {key}")
        Console.msg(f"    Location: {location}")
        Console.msg(f"    Timeout:  {timeout}")
        Console.msg(f"    Secgroup: {secgroup}")
        Console.msg(f"    Group:    {group}")
        Console.msg(f"    Groups:   {groups}")
        Console.msg("")

        try:
            server = self.cloudman.create_server(name,
                                                 flavor=size,
                                                 image=image,
                                                 key_name=key,
                                                 security_groups=[secgroup],
                                                 timeout=timeout
                                                 # tags=groups,
                                                 # wait=True
                                                 )
            server['user'] = user
            r = self.cloudman.wait_for_server(server)
            s = self.cloudman.add_ips_to_server(server, ips=ip)
            variables = Variables()
            variables['vm'] = name
            if metadata is None:
                metadata = {}

            metadata['image'] = image
            metadata['flavor'] = size

            self.cloudman.set_server_metadata(server, metadata)

            self.add_secgroup(name=secgroup)

            # server = self.cloudman.compute.wait_for_server(server)

            # print("ssh -i {key} root@{ip}".format(
            #    key=PRIVATE_KEYPAIR_FILE,
            #    ip=server.access_ipv4))

        except openstack.exceptions.ResourceTimeout:
            Console.error("Problem starting vm in time.")
            raise TimeoutError


        except Exception as e:
            Console.error("Problem starting vm", traceflag=True)
            print(e)
            raise RuntimeError

        return self.update_dict(server, kind="vm")[0]

    # ok
    def list_public_ips(self,
                        ip=None,
                        available=False):

        if ip is not None:
            ips = self.cloudman.list_floating_ips({'floating_ip_address': ip})
        else:
            ips = self.cloudman.list_floating_ips()
            if available:
                found = []
                for entry in ips:
                    if entry['fixed_ip_address'] is None:
                        found.append(entry)
                ips = found

        return self.update_dict(ips, kind="ip")

    # ok
    def delete_public_ip(self, ip=None):
        try:
            if ip is None:
                ips = self.cloudman.list_floating_ips(available=True)
            else:
                ips = self.cloudman.list_floating_ips(
                    {'floating_ip_address': ip})
            for _ip in ips:
                r = self.cloudman.delete_floating_ip(_ip['id'])
        except:
            pass

    # ok
    def create_public_ip(self):
        return self.cloudman.create_floating_ip()

    # ok
    def find_available_public_ip(self):
        entry = self.cloudman.available_floating_ip()
        ip = entry['floating_ip_address']
        return ip

    # ok
    def attach_public_ip(self, name=None, ip=None):
        server = self.cloudman.get_server(name)
        return self.cloudman.add_ips_to_server(server, ips=ip)

    # ok
    def detach_public_ip(self, name=None, ip=None):
        server = self.cloudman.get_server(name)['id']
        data = self.cloudman.list_floating_ips({'floating_ip_address': ip})[0]
        ip_id = data['id']
        return self.cloudman.detach_ip_from_server(server_id=server,
                                                   floating_ip_id=ip_id)

    # ok
    def get_public_ip(self,
                      server=None,
                      name=None):
        if not server:
            server = self.info(name=name)
        ip = None
        ips = server['addresses']
        first = list(ips.keys())[0]
        addresses = ips[first]

        for address in addresses:
            if address['OS-EXT-IPS:type'] == 'floating':
                ip = address['addr']
                break
        return ip

    # ok
    def get_private_ip(self,
                       server=None,
                       name=None):
        if not server:
            server = self.info(name=name)
        ip = None
        ips = server['addresses']
        first = list(ips.keys())[0]
        addresses = ips[first]

        found = []
        for address in addresses:
            if address['OS-EXT-IPS:type'] == 'fixed':
                ip = address['addr']
                found.append(ip)
        return found

    def console(self, vm=None):
        server = vm['id']
        return self.cloudman.get_server_console(server=server)

    def log(self, vm=None):
        # same as console!!!!
        server = vm['id']
        return self.cloudman._get_server_console_output(server)

    def rename(self, name=None, destination=None):
        """
        rename a node. NOT YET IMPLEMENTED.

        :param destination
        :param name: the current name
        :return: the dict with the new name
        """
        raise NotImplementedError
        return None

    def ssh(self, vm=None, command=None):
        #
        # TODO: fix user name issue, should be stored in db
        #

        # VERBOSE(vm)

        ip = vm['ip_public']
        key_name = vm['key_name']
        image = vm['metadata']['image']
        user = Image.guess_username(image)

        cm = CmDatabase()

        keys = cm.find_all_by_name(name=key_name, kind="key")
        for k in keys:
            if 'location' in k.keys():
                if 'private' in k['location'].keys():
                    key = k['location']['private']
                    break

        cm.close_client()

        if command is None:
            command = ""

        if user is None:
            location = ip
        else:
            location = user + '@' + ip
        cmd = "ssh " \
              "-o StrictHostKeyChecking=no " \
              "-o UserKnownHostsFile=/dev/null " \
              f"-i {key} {location} {command}"
        cmd = cmd.strip()
        # VERBOSE(cmd)

        if command == "":
            if platform.lower() == 'win32':
                class disable_file_system_redirection:
                    _disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
                    _revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection

                    def __enter__(self):
                        self.old_value = ctypes.c_long()
                        self.success = self._disable(
                            ctypes.byref(self.old_value))

                    def __exit__(self, type, value, traceback):
                        if self.success:
                            self._revert(self.old_value)

                with disable_file_system_redirection():
                    os.system(cmd)
            else:
                os.system(cmd)
        else:
            if platform.lower() == 'win32':
                class disable_file_system_redirection:
                    _disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
                    _revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection

                    def __enter__(self):
                        self.old_value = ctypes.c_long()
                        self.success = self._disable(
                            ctypes.byref(self.old_value))

                    def __exit__(self, type, value, traceback):
                        if self.success:
                            self._revert(self.old_value)

                with disable_file_system_redirection():
                    ssh = subprocess.Popen(cmd,
                                           shell=True,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
            else:
                ssh = subprocess.Popen(cmd,
                                       shell=True,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            result = ssh.stdout.read().decode("utf-8")
            if not result:
                error = ssh.stderr.readlines()
                print("ERROR: %s" % error)
            else:
                return result

    def wait(self,
             vm=None,
             interval=None,
             timeout=None):
        name = vm['name']
        if interval is None:
            # if interval is too low, OS will block your ip (I think)
            interval = 10
        if timeout is None:
            timeout = 360
        Console.info(
            f"waiting for instance {name} to be reachable: Interval: {interval}, Timeout: {timeout}")
        timer = 0
        while timer < timeout:
            sleep(interval)
            timer += interval
            try:
                r = self.list()
                r = self.ssh(vm=vm, command='echo IAmReady').strip()
                if 'IAmReady' in r:
                    return True
            except:
                pass

        return False
