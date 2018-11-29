from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from cm4.vm.Cloud import Cloud
from cm4.configuration.config import Config

from libcloud.compute.drivers.ec2 import EC2NodeDriver
from libcloud.compute.base import NodeDriver


class Cmaws(Cloud):

    def __init__(self, config, kind):
        cls = get_driver(Provider.EC2)
        os_config = config.get('cloud.%s' % kind)
        default = os_config.get('default')
        credentials = os_config.get('credentials')
        self.driver = cls(
            credentials['EC2_ACCESS_ID'],
            credentials['EC2_SECRET_KEY'],
            region=default['region']
        )



class CmAWSDriver(EC2NodeDriver, NodeDriver):

    def __init__(self, id, key, region):
        config = Config()
        self.default = config.get("cloud.aws.default")

        super().__init__(key=id, secret=key, region=region)

    def start(self, node):
        self.ex_start_node(node)


    def stop(self, node):
        self.ex_stop_node(node)


    def destroy_node(self, node):
        self.destroy_node(node)


    def create_node(self, name):
        size = [s for s in self.list_sizes() if s.id == self.default['size']][0]
        image = [i for i in self.list_images() if i.id == self.default['image']][0]
        new_vm = self.create_node(name=name, image=image, size=size, ex_keyname=self.default['EC2_PRIVATE_KEY_FILE_NAME'],
                             ex_securitygroup=self.default['EC2_SECURITY_GROUP'])

        return new_vm

