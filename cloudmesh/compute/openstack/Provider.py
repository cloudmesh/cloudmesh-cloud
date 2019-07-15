import subprocess
from datetime import datetime
from pprint import pprint

import openstack
from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.management.configuration.config import Config
from cloudmesh.provider import ComputeProviderPlugin

class Provider(ComputeNodeABC, ComputeProviderPlugin):

    kind = "openstack"

    output = {

        "vm": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.cloud",
                      "vm_state",
                      "status",
                      "image",
                      "public_ips",
                      "private_ips",
                      "project_id",
                      "launched_at",
                      "cm.kind"],
            "header": ["Name",
                       "Cloud",
                       "State",
                       "Status",
                       "Image",
                       "Public IPs",
                       "Private IPs",
                       "Project ID",
                       "Started at",
                       "Kind"]
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
        "secgroup": {
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
        }
    }

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
             'project_id': config['OS_TENANT_NAME'],
             'region_name': config['OS_REGION_NAME'],
             'tenant_id': config['OS_TENANT_ID']}
        # d['project_domain_name'] = config['OS_PROJECT_NAME']
        return d

    def __init__(self, name=None, configuration="~/.cloudmesh/cloudmesh4.yaml"):
        """
        Initializes the provider. The default parameters are read from the
        configurationfile that is defined in yaml format.

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
            Console.error("The password TBD is not allowed")
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
                             "provile of the yaml file.")

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

            if kind == 'key':
                try:
                    entry['comment'] = entry['public_key'].split(" ",2)[2]
                except:
                    entry['comment'] = ""
                entry['format'] = \
                    entry['public_key'].split(" ", 1)[0].replace("ssh-","")

            entry["cm"] = {
                "kind": kind,
                "driver": self.cloudtype,
                "cloud": self.cloud,
                "name": entry['name']
            }
            if kind == 'vm':
                entry["cm"]["updated"] = str(datetime.utcnow())
                if "created_at" in entry:
                    entry["cm"]["created"] = str(entry["created_at"])
                    # del entry["created_at"]
                else:
                    entry["cm"]["created"] = entry["modified"]
            elif kind == 'flavor':
                entry["cm"]["created"] = entry["updated"] = str(
                    datetime.utcnow())

            elif kind == 'image':
                entry['cm']['created'] = str(datetime.utcnow())
                entry['cm']['updated'] = str(datetime.utcnow())
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
            if  element["name"] == name or element["cm"]["name"] == name:
                return element
        return None

    def keys(self):
        """
        Lists the keys on the cloud

        :return: dict or libcloud object
        """
        return self.get_list(self.cloudman.list_keypairs(),
                             kind="key")


    def key_upload(self, key):
        """
        uploads the key specified in the yaml configuration to the cloud
        :param key:
        :return:
        """

        name = key["name"]
        cloud = self.cloud
        Console.msg(f"upload the key: {name} -> {cloud}")
        try:
            r = self.cloudman.create_keypair(name,key['string'])
        except openstack.exceptions.ConflictException:
            raise ValueError(f"key already exists: {name}")

        return r

    def key_delete(self, name):
        """
        deletes the key with the given name
        :param name: The anme of the key
        :return:
        """

        cloud = self.cloud
        Console.msg(f"delete the key: {name} -> {cloud}")
        r = self.cloudman.delete_keypair(name)

        return r

    def list_secgroups(self, secgroup=None):

        # TODO: implement group as Parameter
        #  retuns all groups at this time

        return self.get_list(
            self.cloudman.network.security_groups(),
            kind="secgroup")

    def list_secgroup_rules(self, secgroup='default'):

        # TODO: implement group as Parameter
        #  retuns all groups at this time

        return self.list_secgroups()

    def add_secgroup(self, name, description=None):
        """
        Adds the
        :param name:
        :param description:
        :return:
        """
        if self.cloudman:
            self.cloudman.create_security_group(name,
                                                description)

    def remove_secgroup(self, name):
        if self.cloudman:
            self.cloudman.delete_security_group(name)

    def add_rules_to_secgroup(self, secgroupname, newrules):
        raise NotImplementedError
        oldrules = self.list_secgroup_rules(secgroupname)
        pprint(oldrules)
        pprint(newrules)
        if self.cloudman:
            secgroups = self.list_secgroups()
            for secgroup in secgroups:
                # for multiple secgroups with the same name,
                # add the rules to all the groups
                if secgroup.name == secgroupname:
                    # supporting multiple rules at once
                    for rule in newrules:
                        self.cloudman.ex_create_security_group_rule(secgroup,
                                                                    rule[
                                                                        "ip_protocol"],
                                                                    rule[
                                                                        "from_port"],
                                                                    rule[
                                                                        "to_port"],
                                                                    cidr=rule[
                                                                        "ip_range"]
                                                                    )

    def remove_rules_from_secgroup(self, secgroupname, rules):
        raise NotImplementedError
        oldrules = self.list_secgroup_rules(secgroupname)
        pprint(oldrules)
        pprint(rules)
        if self.cloudman:
            secgroups = self.list_secgroups()
            for secgroup in secgroups:
                # for multiple secgroups with the same name,
                # remove the rules from all the groups
                if secgroup.name == secgroupname:
                    # supporting multiple rules at once
                    # get all rules, in obj format
                    rulesobj = self.list_secgroup_rules(secgroup=secgroupname)
                    for rule in rules:
                        for ruleobj in rulesobj:
                            if (ruleobj.ip_protocol == rule["ip_protocol"] and
                                ruleobj.from_port == rule["from_port"] and
                                ruleobj.to_port == rule["to_port"] and
                                ruleobj.ip_range == rule["ip_range"]):
                                self.cloudman.ex_delete_security_group_rule(
                                    ruleobj)

    def get_list(self, d, kind=None, debug=False, **kwargs):
        """
        Lists the dict d on the cloud
        :return: dict or libcloud object
        """

        if self.cloudman:
            entries = []
            for entry in d:
                entries.append(dict(entry))
            if debug:
                pprint(entries)

            return self.update_dict(entries, kind=kind)
        return None

    def images(self, **kwargs):
        """
        Lists the images on the cloud
        :return: dict or libcloud object
        """
        return self.get_list(self.cloudman.compute.images(),
                             kind="image")

    def image(self, name=None, **kwargs):
        """
        Gets the image with a given nmae
        :param name: The name of the image
        :return: the dict of the image
        """
        return self.find(self.images(**kwargs), name=name)

    def flavors(self):
        """
        Lists the flavors on the cloud

        :return: dict of flavors
        """
        return self.get_list(self.cloudman.compute.flavors(),
                             kind="flavor")

    def flavor(self, name=None):
        """
        Gest the flavor with a given name
        :param name: The name of the flavor
        :return: The dict of the flavor
        """
        return self.find(self.flavors(), name=name)

    def apply(self, fname, names):
        """
        apply a function to a given list of nodes

        :param fname: Name of the function to be applied to the given nodes
        :param names: A list of node names
        :return:  A list of dict representing the nodes
        """
        raise NotImplementedError
        if self.cloudman:
            # names = Parameter.expand(names)
            res = []

            nodes = self.list()
            for node in nodes:
                if node.name in names:
                    fname(node)
                    res.append(self.info(node.name))
            return res
        else:
            return None

    def start(self, name=None):
        """
        Start a server with the given names

        :param names: A list of node names
        :return:  A list of dict representing the nodes
        """
        r = self.cloudman.suspend_server(name)
        #return self.apply(self.cloudman.ex_start_node, names)

    def stop(self, name=None):
        """
        Stop a list of nodes with the given names

        :param names: A list of node names
        :return:  A list of dict representing the nodes
        """
        r = self.cloudman.suspend_server(name)
        # return self.apply(self.cloudman.ex_stop_node, names)
        return None

    def info(self, name=None):
        """
        Gets the information of a node with a given name

        :param name: The name of teh virtual machine
        :return: The dict representing the node including updated status
        """
        self.cloudman.get_server(name)
        #return self.find(self.list(), name=name)

    def suspend(self, name=None):
        """
        NOT YET IMPLEMENTED.

        suspends the node with the given name.

        :param name: the name of the node
        :return: The dict representing the node
        """
        # UNTESTED
        r = self.cloudman.suspend_server(name)
        return None

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
        raise NotImplementedError
        # the following does not return the dict
        return self.apply(self.cloudman.ex_start_node, name)

    def list(self):
        """
        Lists the vms on the cloud

        :return: dict of vms
        """
        return self.get_list(self.cloudman.compute.servers(),
                             kind="vm")

    def destroy(self, name=None):
        """
        Destroys the node
        :param names: the name of the node
        :return: the dict of the node
        """
        r = self.cloudman.delet_server(name)
        # bug status should change to destroyed
        return None

    def reboot(self, names=None):
        """
        Reboot a list of nodes with the given names

        :param names: A list of node names
        :return:  A list of dict representing the nodes
        """
        raise NotImplementedError
        return self.apply(self.cloudman.reboot_node, names)

    def create(self,
               name=None,
               image=None,
               size=None,
               location=None,
               timeout=360,
               key=None,
               secgroup=None,
               **kwargs):
        """
        creates a named node

        :param name: the name of the node
        :param image: the image used
        :param size: the size of the image
        :param timeout: a timeout in seconds that is invoked in case the image
                        does not boot. The default is set to 3 minutes.
        :param kwargs: additional arguments HEADING(c=".")ed along at time of boot
        :return:
        """
        image_use = None
        flavor_use = None

        # keyname = Config()["cloudmesh"]["profile"]["user"]
        # ex_keyname has to be the registered keypair name in cloud

        """
        images = self.images()
        for _image in images:
            if _image.name == image:
                image_use = _image
                break

        flavors = self.flavors()
        for _flavor in flavors:
            if _flavor.name == size:
                flavor_use = _flavor
                break
        """
        print("Create Server:")

        print (image)
        size = kwargs['flavor']

        print (size)



        #_image = self.cloudman.compute.find_image(image)
        #_flavor = self.cloudman.compute.find_flavor(size)
        # network = self.cloudman.network.find_network(NETWORK_NAME)
        # keypair = create_keypair(self.cloudman)




        try:
            server = self.cloudman.create_server(name,
                                            flavor=size,
                                            image=image)


            #server = self.cloudman.compute.create_server(
            #    name=name,
            #    image_id=_image.id,
            #    flavor_id=_flavor.id
            #    # networks=[{"uuid": network.id}],
            #    # key_name=keypair.name
            #)

            # server = self.cloudman.compute.wait_for_server(server)

            # print("ssh -i {key} root@{ip}".format(
            #    key=PRIVATE_KEYPAIR_FILE,
            #    ip=server.access_ipv4))

            # self.cloudman.add_security_group(security_group=secgroup)
        except Exception as e:
            print (e)
            raise NotImplementedError

        return self.update_dict(server, kind="vm")[0]

    def get_publicIP(self):
        # pools = self.cloudman.ex_list_floating_ip_pools()
        # ex_get_floating_ip(ip)
        # ex_create_floating_ip(ip_pool=pools[0])
        #
        """
                    ex_attach_floating_ip_to_node(node, ip)
                    ex_detach_floating_ip_from_node(node, ip)
                    ex_delete_floating_ip(ip)
        """
        raise NotImplementedError
        ip = None
        ips = self.cloudman.ex_list_floating_ips()
        if ips:
            ip = ips[0]
        else:
            pools = self.cloudman.ex_list_floating_ip_pools()
            # pprint (pools)
            # ex_get_floating_ip(ip)
            ip = self.cloudman.ex_create_floating_ip(ip_pool=pools[0].name)

        return ip

    def attach_publicIP(self, node, ip):
        raise NotImplementedError
        return self.cloudman.ex_attach_floating_ip_to_node(node, ip)

    def detach_publicIP(self, node, ip):
        raise NotImplementedError
        self.cloudman.ex_detach_floating_ip_from_node(node, ip)
        return self.cloudman.ex_delete_floating_ip(ip)

    def rename(self, name=None, destination=None):
        """
        rename a node. NOT YET IMPLEMENTED.

        :param destination:
        :param name: the current name
        :return: the dict with the new name
        """
        # if destination is None, increase the name counter and use the new name
        raise NotImplementedError
        return None

    def ssh(self, name=None, command=None):
        raise NotImplementedError
        key = self.key_path.replace(".pub", "")
        nodes = self.list()
        for node in nodes:
            if node.name == name:
                break
        #
        # bug testnode is not defined
        #
        pubip = self.testnode.public_ips[0]
        location = self.user + '@' + pubip
        cmd = ['ssh',
               "-o", "StrictHostKeyChecking=no",
               "-o", "UserKnownHostsFile=/dev/null",
               '-i', key, location, command]
        VERBOSE(" ".join(cmd))

        ssh = subprocess.Popen(cmd,
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        result = ssh.stdout.readlines()
        if result == []:
            error = ssh.stderr.readlines()
            print("ERROR: %s" % error)
        else:
            print("RESULT:")
            for line in result:
                line = line.decode("utf-8")
                print(line.strip("\n"))
