import subprocess
import sys
from datetime import datetime
from pathlib import Path
from pprint import pprint

from cloudmesh.common.debug import VERBOSE
from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.common.console import Console
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand
from cloudmesh.management.configuration.config import Config
import openstack

class Provider(ComputeNodeABC):

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
        "image": {"sort_keys": ["cm.name",
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
                             "Driver"]},
        "flavor": {"sort_keys": ["cm.name",
                                 "vcpus",
                                 "disk"],
                   "order": ["cm.name",
                             "vcpus",
                             "ram",
                             "disk"],
                   "header": ["Name",
                              "VCPUS",
                              "RAM",
                              "Disk"]}

    }

    @staticmethod
    def _get_credentials(config):
        d = {}
        d['version'] = '2'
        d['username'] = config['OS_USERNAME']
        d['password'] = config['OS_PASSWORD']
        # while libcloud uses token, here we do not use it in auth_url
        d['auth_url'] = config['OS_AUTH_URL'].replace("/tokens", "")
        d['project_id'] = config['OS_TENANT_NAME']
        d['region_name'] = config['OS_REGION_NAME']
        # d['project_domain_name'] = config['OS_PROJECT_NAME']
        d['tenant_id'] = config['OS_TENANT_ID']
        return d

    def __init__(self, name=None, configuration="~/.cloudmesh/cloudmesh4.yaml"):
        """
        Initializes the provider. The default parameters are read from the configutation
        file that is defined in yaml format.
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
        credential = self._get_credentials(self.cred)



        connection = openstack.connect(**credential)
        self.cloudman = connection.compute



        # self.default_image = deft["image"]
        # self.default_size = deft["size"]
        # self.default.location = cred["datacenter"]

        try:
            self.public_key_path = conf["profile"]["publickey"]
            self.key_path = path_expand(Config()["cloudmesh"]["profile"]["publickey"])
            f = open(self.key_path, 'r')
            self.key_val = f.read()
        except:
            raise ValueError("the public key location is not set in the "
                             "provile of the yaml file.")

    def update_dict(self, elements, kind=None):
        """
        Libcloud returns an object or list of objects With the dict method
        this object is converted to a dict. Typically this method is used internally.
        :param elements: the elements
        :param kind: Kind is image, flavor, or node
        :return:
        """
        if elements is None:
            return None
        elif type(elements) == list:
            _elements = elements
        else:
            _elements = [elements]
        d = []
        for entry in _elements:

            entry["cm"] = {
                "kind": kind,
                "driver": self.cloudtype,
                "cloud": self.cloud,
                "name": entry['name']
            }
            if kind == 'vm' or kind == 'node':
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
            elif kind == 'secgroup':
                pass
            elif kind == 'key':
                pass

            d.append(entry)
        return d

    def find(self, elements, name=None, raw=False):
        """
        finds an element in elements with the specified name
        :param elements: The elements
        :param name: The name to be found
        :param: If raw is True, elements is a libcloud object.
                Otherwise elements is a dict
        :param raw: if raw is used the return from the driver is used and not a cleaned dict, not implemented
        :return:
        """
        for element in elements:
            # pprint (element)
            if (raw and element.name) or element["cm"]["name"] == name:
                return element
        return None

    def keys(self, raw=False):
        """
        Lists the keys on the cloud
        :param raw: If raw is set to True the lib cloud object is returened
                    otherwise a dict is returened.
        :return: dict or libcloud object
        """
        if self.cloudman:
            entries = self.cloudman.list_key_pairs()
            if raw:
                return entries
            else:
                return self.update_dict(entries, kind="key")
        return None

    def key_upload(self, key):
        """
        uploads the key specified in the yaml configuration to the cloud
        :param key:
        :return:
        """

        #
        # TODO: if you have a key in the local machine that is different from an
        # already uploaded ky this function will fail. The key in the cloud
        # needs to be removed first
        #
        keys = self.keys()
        for cloudkey in keys:
            pprint(cloudkey)
            if cloudkey['fingerprint'] == key["fingerprint"]:
                return

        filename = Path(key["path"])
        key = self.cloudman.import_key_pair_from_file(
            "{user}".format(**self.user), filename)

    def list_secgroups(self, raw=False):
        if self.cloudman:
            secgroups = self.cloudman.ex_list_security_groups()
            if not raw:
                secgroups = self.update_dict(secgroups, kind="secgroup")
            return secgroups
        return None

    def list_secgroup_rules(self, secgroup='default', raw=False):
        if self.cloudman:
            secgroups = self.list_secgroups(raw=raw)
            thegroup = None
            if raw:
                # Theoretically it's possible to have secgroups with the same name,
                # in this case, we list rules for the first one only.
                # In reality this don't seem like a good practice so we assume
                # this situation MOST LIKELY does not occur.
                for _secgroup in secgroups:
                    if _secgroup.name == secgroup:
                        thegroup = _secgroup
                        break
            else:
                # this already returns only one entry
                thegroup = self.find(secgroups, name=secgroup)

            rules = []
            if raw:
                # dealing with object
                for rule in thegroup.rules:
                    rules.append(rule)
            else:
                # dealing with dict
                for rule in thegroup["rules"]:
                    # self.p.dict() converted the object into a list of dict,
                    # even if there is only one object
                    rule = self.update_dict(rule)[0]
                    rules.append(rule)
            return rules
        return None

    def add_secgroup(self, secgroupname, description=""):
        if self.cloudman:
            return self.cloudman.ex_create_security_group(secgroupname,
                                                          description=description)
        return None

    def remove_secgroup(self, secgroupname):
        if self.cloudman:
            secgroups = self.list_secgroups(raw=True)
            thegroups = []
            for secgroup in secgroups:
                if secgroup.name == secgroupname:
                    thegroups.append(secgroup)
            # pprint (secgroups)
            # pprint (thegroups)
            if thegroups:
                for thegroup in thegroups:
                    self.cloudman.ex_delete_security_group(thegroup)
            else:
                return False
        return False

    def add_rules_to_secgroup(self, secgroupname, newrules):
        oldrules = self.list_secgroup_rules(secgroupname)
        pprint(oldrules)
        pprint(newrules)
        if self.cloudman:
            secgroups = self.list_secgroups(raw=True)
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
        oldrules = self.list_secgroup_rules(secgroupname)
        pprint(oldrules)
        pprint(rules)
        if self.cloudman:
            secgroups = self.list_secgroups(raw=True)
            for secgroup in secgroups:
                # for multiple secgroups with the same name,
                # remove the rules from all the groups
                if secgroup.name == secgroupname:
                    # supporting multiple rules at once
                    # get all rules, in obj format
                    rulesobj = self.list_secgroup_rules(secgroup=secgroupname,
                                                        raw=True)
                    for rule in rules:
                        for ruleobj in rulesobj:
                            if (ruleobj.ip_protocol == rule["ip_protocol"] and
                                ruleobj.from_port == rule["from_port"] and
                                ruleobj.to_port == rule["to_port"] and
                                ruleobj.ip_range == rule["ip_range"]):
                                self.cloudman.ex_delete_security_group_rule(
                                    ruleobj)

    def get_list(self, d, kind=None, raw=False, **kwargs):
        """
        Lists the images on the cloud
        :param raw: If raw is set to True the lib cloud object is returned
                    otherwise a dict is returened.
        :return: dict or libcloud object
        """
        if self.cloudman:

            all = self.cloudman.images()
            entries = []
            for entry in d:
                entries.append(dict(entry))
            if raw:
                return entries
            else:
                return self.update_dict(entries, kind=kind)

        return None

    def images(self, raw=False, **kwargs):
        """
        Lists the images on the cloud
        :param raw: If raw is set to True the lib cloud object is returned
                    otherwise a dict is returened.
        :return: dict or libcloud object
        """
        return self.get_list(self.cloudman.images(),kind="images", raw=raw)

    def image(self, name=None, **kwargs):
        """
        Gets the image with a given nmae
        :param name: The name of the image
        :return: the dict of the image
        """
        return self.find(self.images(raw=False, **kwargs), name=name)

    def flavors(self, raw=False):
        """
        Lists the flavors on the cloud
        :param raw: If raw is set to True the lib cloud object is returned
                    otherwise a dict is returened.
        :return: dict or libcloud object
        """
        return self.get_list(self.cloudman.flavors(),kind="flavor", raw=raw)

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
        if self.cloudman:
            # names = Parameter.expand(names)
            res = []

            nodes = self.list(raw=True)
            for node in nodes:
                if node.name in names:
                    fname(node)
                    res.append(self.info(node.name))
            return res
        else:
            return None

    def start(self, names=None):
        """
        Start a list of nodes with the given names

        :param names: A list of node names
        :return:  A list of dict representing the nodes
        """
        VERBOSE(names)
        return self.apply(self.cloudman.ex_start_node, names)

    def stop(self, names=None):
        """
        Stop a list of nodes with the given names

        :param names: A list of node names
        :return:  A list of dict representing the nodes
        """

        return self.apply(self.cloudman.ex_stop_node, names)

    def info(self, name=None):
        """
        Gets the information of a node with a given name

        :param name: The name of teh virtual machine
        :return: The dict representing the node including updated status
        """
        return self.find(self.list(), name=name)

    def suspend(self, name=None):
        """
        NOT YET IMPLEMENTED.

        suspends the node with the given name.

        :param name: the name of the node
        :return: The dict representing the node
        """

        return None

        """
        raise NotImplementedError

        #
        # BUG THIS CODE DOES NOT WORK
        #
        nodes = self.list(raw=True)
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

        # the following does not return the dict
        return self.apply(self.cloudman.ex_start_node, name)

    def list(self, raw=False):
        """
        Lists the vms on the cloud
        :param raw: If raw is set to True the lib cloud object is returned
                    otherwise a dict is returened.
        :return: dict or libcloud object
        """
        return self.get_list(self.cloudman.servers(), kind="node", raw=raw)


    def destroy(self, names=None):
        """
        Destroys the node
        :param names: the name of the node
        :return: the dict of the node
        """
        # names = Parameter.expand(names)

        nodes = self.list(raw=True)
        for node in nodes:
            if node.name in names:
                self.cloudman.destroy_node(node)
        # bug status should change to destroyed
        return None

    def reboot(self, names=None):
        """
        Reboot a list of nodes with the given names

        :param names: A list of node names
        :return:  A list of dict representing the nodes
        """
        return self.apply(self.cloudman.reboot_node, names)

    def create(self,
               name=None,
               image=None,
               size=None,
               location=None,
               timeout=360,
               key=None,
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

        images = self.images(raw=True)
        for _image in images:
            if _image.name == image:
                image_use = _image
                break

        flavors = self.flavors(raw=True)
        for _flavor in flavors:
            if _flavor.name == size:
                flavor_use = _flavor
                break

        if "ex_security_groups" in kwargs:
            secgroupsobj = []
            #
            # this gives existing secgroups in obj form
            secgroups = self.list_secgroups(raw=True)
            for secgroup in kwargs["ex_security_groups"]:
                for _secgroup in secgroups:
                    if _secgroup.name == secgroup:
                        secgroupsobj.append(_secgroup)
            # now secgroup name is converted to object which
            # is required by the libcloud api call
            kwargs["ex_security_groups"] = secgroupsobj


        raise NotImplementedError

        #return self.update_dict(node, kind="node")[0]
        return None

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
        return self.cloudman.ex_attach_floating_ip_to_node(node, ip)

    def detach_publicIP(self, node, ip):
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
        HEADING(c=".")
        return None

    def ssh(self, name=None, command=None):
        key = self.key_path.replace(".pub", "")
        nodes = self.list(raw=True)
        for node in nodes:
            if node.name == name:
                self.testnode = node
                break
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

