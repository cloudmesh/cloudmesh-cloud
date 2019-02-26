import sys
from datetime import datetime
from pathlib import Path
from pprint import pprint

from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider as LibcloudProvider

from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import HEADING
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.util import path_expand


class Provider(ComputeNodeABC):
    # ips
    # secgroups
    # keys

    ProviderMapper = {
        "openstack": LibcloudProvider.OPENSTACK,
        "aws": LibcloudProvider.EC2,
        "azure_asm": LibcloudProvider.AZURE,
        "azure_arm": LibcloudProvider.AZURE_ARM
    }

    def __init__(self, name=None, configuration="~/.cloudmesh/cloudmesh4.yaml"):
        """
        Initializes the provider. The default parameters are read from the configutation
        file that is defined in yaml format.

        :param name: The name of the provider as defined in the yaml file
        :param configuration: The location of the yaml configuration filw
        """
        HEADING(c=".")
        conf = Config(configuration)["cloudmesh"]
        self.user = conf["profile"]
        self.spec = conf["cloud"][name]
        self.cloud = name
        cred = self.spec["credentials"]
        self.cloudtype = self.spec["cm"]["kind"]
        super().__init__(name, conf)

        pprint(Provider.ProviderMapper)

        if self.cloudtype in Provider.ProviderMapper:

            self.driver = get_driver(
                Provider.ProviderMapper[self.cloudtype])

            if self.cloudtype == 'openstack':
                self.cloudman = self.driver(cred["OS_USERNAME"],
                                            cred["OS_PASSWORD"],
                                            ex_force_auth_url=cred[
                                                'OS_AUTH_URL'],
                                            ex_force_auth_version='2.0_password',
                                            ex_tenant_name=cred[
                                                'OS_TENANT_NAME'])
            elif self.cloudtype == 'azure_asm':

                self.cloudman = self.driver(
                    subscription_id=cred['AZURE_SUBSCRIPTION_ID'],
                    key_file=path_expand(cred['AZURE_KEY_FILE'])

                )

            elif self.cloudtype == 'aws':

                self.cloudman = self.driver(
                    cred["EC2_ACCESS_ID"],
                    cred["EC2_SECRET_KEY"],
                    region=cred["region"])
        else:
            print("Specified provider not available")
            self.cloudman = None
        self.default_image = None
        self.default_size = None
        self.public_key_path = conf["profile"]["publickey"]

    def dict(self, elements, kind=None):
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
        for element in _elements:
            entry = element.__dict__
            entry["kind"] = kind
            entry["driver"] = self.cloudtype
            entry["cloud"] = self.cloud

            if kind == 'node':
                entry["updated"] = str(datetime.utcnow())

                if "created_at" in entry:
                    entry["created"] = str(entry["created_at"])
                    del entry["created_at"]
                else:
                    entry["created"] = entry["modified"]
            elif kind == 'flavor':
                entry["created"] = entry["updated"] = str(datetime.utcnow())
            elif kind == 'image':
                if self.cloudtype == 'openstack':
                    entry['created'] = entry['extra']['created']
                    entry['updated'] = entry['extra']['updated']
                else:
                    pass

            if "_uuid" in entry:
                del entry["_uuid"]

            d.append(entry)
        return d

    def find(self, elements, name=None):
        """
        finds an element in elements with the specified name
        :param elements: The elements
        :param name: The name to be found
        :return:
        """
        for element in elements:
            if element["name"] == name:
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
                return self.dict(entries, kind="key")
        return None

    def key_upload(self, key):
        """
        uploades teh key specified in the yaml configuration to the cloud
        :param key:
        :return:
        """

        print(key)
        keys = self.keys()
        for cloudkey in keys:
            if cloudkey['fingerprint'] == key["fingerprint"]:
                return

        filename = Path(key["path"])
        key = self.cloudman.import_key_pair_from_file(
            "{user}".format(**self.user), filename)

    def list_secgroups(self, raw=False):
        if self.cloudman:
            secgroups = self.cloudman.ex_list_security_groups()
            if not raw:
                secgroups = self.dict(secgroups, kind="secgroup")
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
                    rule = self.dict(rule)[0]
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

    def images(self, raw=False):
        """
        Lists the images on the cloud
        :param raw: If raw is set to True the lib cloud object is returened
                    otherwise a dict is returened.
        :return: dict or libcloud object
        """
        if self.cloudman:
            entries = self.cloudman.list_images()
            if raw:
                return entries
            else:
                return self.dict(entries, kind="image")

        return None

    def image(self, name=None):
        """
        Gets the image with a given nmae
        :param name: The name of the image
        :return: the dict of the image
        """
        return self.find(self.images(), name=name)

    def flavors(self, raw=False):
        """
        Lists the flavors on the cloud
        :param raw: If raw is set to True the lib cloud object is returened
                    otherwise a dict is returened.
        :return: dict or libcloud object
        """
        if self.cloudman:
            entries = self.cloudman.list_sizes()
            if raw:
                return entries
            else:
                return self.dict(entries, kind="flavor")
        return None

    def flavor(self, name=None):
        """
        Gest the flavor with a given name

        :param name: The aname of the flavor
        :return: The dict of the flavor
        """
        return self.find(self.flavors(), name=name)

    def start(self, name=None):
        """
        start a node. NOT YET IMPLEMENTED.
    
        :param name: the unique node name
        :return:  The dict representing the node
        """
        HEADING(c=".")
        return None

    def stop(self, name=None):
        """
        stops the node with the given name. NOT YET IMPLEMENTED.
    
        :param name:
        :return: The dict representing the node including updated status
        """
        HEADING(c=".")
        return None

    def info(self, name=None):
        """
        Gets the information of a node with a given name
    
        :param name: The name of teh virtual machine
        :return: The dict representing the node including updated status
        """
        return self.find(self.list(), name=name)

    def suspend(self, name=None):
        """
        suspends the node with the given name. NOT YET IMPLEMENTED.
    
        :param name: the name of the node
        :return: The dict representing the node
        """
        HEADING(c=".")
        return None

    def list(self, raw=False):
        """
        Lists the vms on the cloud
        :param raw: If raw is set to True the lib cloud object is returened
                    otherwise a dict is returened.
        :return: dict or libcloud object
        """
        if self.cloudman:
            if self.cloudtype == "azure_asm":
                #
                # BUG: ex_cloud_service_name needs to be defined, explore the
                # azure documentation n how to find it
                #
                entries = self.cloudman.list_nodes()
            elif self.cloudtype == "azure_arm":
                #
                # BUG: figure out how to use that
                #
                entries = self.cloudman.list_nodes()
            else:
                entries = self.cloudman.list_nodes()
            if raw:
                return entries
            else:
                return self.dict(entries, kind="node")
        return None

    def resume(self, name=None):
        """
        resume the named node. NOT YET IMPLEMENTED.
    
        :param name: the name of the node
        :return: the dict of the node
        """
        HEADING(c=".")
        return None

    def destroy(self, names=None):
        """
        Destroys the node
        :param names: the name of the node
        :return: the dict of the node
        """

        names = Parameter.expand(names)

        nodes = self.list(raw=True)
        for node in nodes:
            if node.name in names:
                self.cloudman.destroy_node(node)
        # bug status shoudl change to destroyed
        return None

    def reboot(self, name=None):
        """
        Reboot the node. NOT YET IMPLEMENTED.

        :param name: the name of the node
        :return: the dict of the node
        """
        HEADING(c=".")
        return None

    def create(self, name=None, image=None, size=None, timeout=360, **kwargs):
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
        images = self.images(raw=True)
        image_use = None
        flavors = self.flavors(raw=True)
        flavor_use = None
        for _image in images:
            if _image.name == image:
                image_use = _image
                break
        for _flavor in flavors:
            if _flavor.name == size:
                flavor_use = _flavor
                break
        # keyname = Config()["cloudmesh"]["profile"]["user"]
        # ex_keyname has to be the registered keypair name in cloud
        pprint(kwargs)
        if self.cloudtype == "openstack":
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
            node = self.cloudman.create_node(name=name, image=image_use,
                                             size=flavor_use, **kwargs)
        else:
            sys.exit("this cloud is not yet supported")

        pprint(node)
        return self.dict(node)

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
        if self.cloudtype == "openstack":
            ips = self.cloudman.ex_list_floating_ips()
            if ips:
                ip = ips[0]
            else:
                pools = self.cloudman.ex_list_floating_ip_pools()
                # ex_get_floating_ip(ip)
                ip = self.cloudman.ex_create_floating_ip(ip_pool=pools[0])
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
