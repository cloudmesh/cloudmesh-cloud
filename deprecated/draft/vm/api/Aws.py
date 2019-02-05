from deprecated.draft.vm.api.Cloud import Cloud
from deprecated.draft.vm.api.LibcloudBaseProvider import LibcloudBaseProvider
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver


class AwsProvider(LibcloudBaseProvider, Cloud):

    def __init__(self, config):
        super().__init__("aws", config)

        cls = get_driver(Provider.EC2)
        self.driver = cls(
            self.credentials['EC2_ACCESS_ID'],
            self.credentials['EC2_SECRET_KEY'],
            region=self.default['region']
        )

    def create(self, name=None, image=None, size=None, timeout=360, **kwargs):
        node = super().create(name=name,
                              image=image,
                              size=size,
                              ex_keyname=self.default['EC2_PRIVATE_KEY_FILE_NAME'],
                              ex_securitygroup=self.default['EC2_SECURITY_GROUP'])
        return node

    def start(self, name):
        node = self.info(name)
        self.driver.ex_start_node(node)
        return node

    def stop(self, name=None):
        node = self.info(name)
        self.driver.ex_stop_node(node)
        return node

    def set_public_ip(self):
        raise NotImplementedError("Set public IP not implemented for aws.")

    def remove_public_ip(self):
        raise NotImplementedError("Remove public IP not implemented for aws.")
