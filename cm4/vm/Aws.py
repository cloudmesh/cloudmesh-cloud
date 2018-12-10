from cm4.vm.Cloud import Cloud
from cm4.configuration.config import Config
from cm4.abstractclass.CloudManagerABC import CloudManagerABC
from libcloud.compute.drivers.ec2 import EC2NodeDriver
from libcloud.compute.base import NodeDriver


class AwsProvider(CloudManagerABC, Cloud):

    def __init__(self, config):
        os_config = config["cloud"]["aws"]
        default = os_config.get('default')
        credentials = os_config.get('credentials')
        self.driver = AWSDriver(
            credentials['EC2_ACCESS_ID'],
            credentials['EC2_SECRET_KEY'],
            region=default['region']
        )

    def start(self, name):
        """

        :param name:
        :return:
        """
        self.driver.ex_start_node(self.driver._get_node(name))

    def stop(self, name=None):
        """
        Stop a running node. Deallocate resources. VM status will
        be `stopped`.
        :param name:
        """
        self.driver.ex_stop_node(self.driver._get_node(name))

    def info(self, name=None):
        """
        gets the information of a node with a given name

        :param name:
        :return: The dict representing the node including updated status
        """
        return self.driver._get_node(name)

    def suspend(self, name=None):
        self.stop(name)

    def nodes(self):
        """
        list all nodes id
        Todo: move to libcloud base manager.
        :return: an array of dicts representing the nodes
        """
        return self.driver.list_nodes()

    def resume(self, name=None):
        self.start(name)

    def destroy(self, name=None):
        self.driver.destroy_node(self.driver._get_node(name))

    def create(self, name=None, image=None, size=None, timeout=360, **kwargs):
        self.driver.create_node(name)

    def set_public_ip(self, name, public_ip):
        print("No set_public_ip method")
        pass

    def remove_public_ip(self, name):
        print("No remove_public_ip method")
        pass


class AWSDriver(EC2NodeDriver, NodeDriver):

    def __init__(self, key, secret, region, **kwargs):
        config = Config().data["cloudmesh"]
        self.default = config["cloud"]["aws"]["default"]
        super().__init__(key=key, secret=secret, region=region, **kwargs)

    def ex_stop_node(self, node, deallocate=None):
        super().ex_stop_node(node)

    def create_node(self, name):
        size = [s for s in self.list_sizes() if s.id == self.default['size']][0]
        image = [i for i in self.list_images() if i.id == self.default['image']][0]
        new_vm = super().create_node(name=name, image=image, size=size,
                                     ex_keyname=self.default['EC2_PRIVATE_KEY_FILE_NAME'],
                                     ex_securitygroup=self.default['EC2_SECURITY_GROUP'])

        return new_vm

    def _get_node(self, name):
        """
        Get an instance of a Node returned by `list` by node name.
        """
        node = [n for n in self.list_nodes() if n.name == name]
        return node[0] if node else None