from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from pprint import pprint
from datetime import datetime
from cloudmesh.common.util import HEADING
from cloudmesh.common.parameter import Parameter
from cloudmesh.management.configuration.config import Config

from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider as LibcloudProvider
from cloudmesh.common.util import path_expand
from pathlib import Path
from cloudmesh.management.configuration.SSHkey import SSHkey
import sys

class Provider(ComputeNodeABC):

    # ips
    # secgroups
    # keys

    ProviderMapper = {
        "openstack": LibcloudProvider.OPENSTACK,
        "aws": LibcloudProvider.EC2
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
        mycloud = conf["cloud"][name]
        cred = mycloud["credentials"]
        self.kind = mycloud["cm"]["kind"]
        #pprint (cred)
        #print (self.kind)
        super().__init__(name, conf)
        if self.kind in Provider.ProviderMapper:
            if self.kind == 'openstack':
                self.driver = get_driver(Provider.ProviderMapper[self.kind])
                self.cloudman = self.driver(cred["OS_USERNAME"],
                                    cred["OS_PASSWORD"],
                                    ex_force_auth_url=cred['OS_AUTH_URL'],
                                    ex_force_auth_version='2.0_password',
                                    ex_tenant_name=cred['OS_TENANT_NAME'])
        else:
            print ("Specified provider not available")
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
            entry["driver"] = self.kind

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
                entry['created'] = entry['extra']['created']
                entry['updated'] = entry['extra']['updated']

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
        key = self.cloudman.import_key_pair_from_file("{user}".format(**self.user), filename)



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

    def start(self, name):
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
        :param name: the name of the node
        :return: the dict of the node
        """

        names = Parameter.expand(names)

        nodes = self.list(raw=True)
        for node in nodes:
            if node.name in names:
                self.cloudman.destroy_node(node)
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
        :param timeout: a timeout in seconds that is invoked in case the image does not boot.
               The default is set to 3 minutes.
        :param kwargs: additional arguments HEADING(c=".")ed along at time of boot
        :return:
        """
        images = self.images(raw=True)
        imageUse = None
        flavors = self.flavors(raw=True)
        flavorUse = None
        for _image in images:
            if _image.name == image:
                imageUse = _image
                break
        for _flavor in flavors:
            if _flavor.name == size:
                flavorUse = _flavor
                break
        keyname = Config()["cloudmesh"]["profile"]["user"]
        if self.kind == "openstack":
            node = self.cloudman.create_node(name=name, image=imageUse, size=flavorUse, ex_keyname=keyname)
        else:
            sys.exit("this cloud is not yet supported")

        pprint (node)
        return (self.dict(node))
        # no brackets needed?

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

