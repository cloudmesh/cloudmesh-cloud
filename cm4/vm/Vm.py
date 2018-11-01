from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from cm4.configuration.config import Config
from libcloud.compute.base import NodeAuthSSHKey


class Provider (object):

    def __init__(self, cloud):
        config = Config()
        self.os_config = config.get('cloud.%s' % cloud)
        self.default = self.os_config.get('default')
        self.credentials = self.os_config.get('credentials')
        self.driver = None
        self.setting = dict()

    # only developed for AZURE, AWS, Chameleon
    def get_provider(self):
        """
        Create the driver based on the 'kind' information.
        This method could deal with AWS, AZURE, and OPENSTACK for CLOUD block of YAML file.
        But we haven't test OPENSTACK
        :return: the driver based on the 'kind' information
        """
        if self.os_config.get('cm.kind') == 'azure':
            cls = get_driver(Provider.AZURE)
            self.driver = cls(tenant_id=self.credentials['AZURE_TENANT_ID'],
                              subscription_id=self.credentials['AZURE_SUBSCRIPTION_ID'],
                              key=self.credentials['AZURE_APPLICATION_ID'],
                              secret=self.credentials['AZURE_SECRET_KEY'],
                              region=self.default['region'])
            size = [s for s in self.driver.list_sizes() if s.id == self.default['size']][0]
            image = [i for i in self.driver.list_images() if i.id == self.default['image']][0]
            self.setting.update(size=size, image=image, auth=NodeAuthSSHKey(self.default['AZURE_MANAGEMENT_CERT_PATH']),
                                ex_use_managed_disks=True, ex_resource_group=self.default['resource_group'],
                                ex_storage_account=self.default['storage_account'],
                                ex_network=self.default['network']
                                )


        elif self.os_config.get('cm.kind') == 'aws':
            cls = get_driver(Provider.EC2)
            self.driver = cls(self.credentials['EC2_ACCESS_ID'],
                              self.credentials['EC2_SECRET_KEY'],
                              self.default['region'])
            size = [s for s in self.driver.list_sizes() if s.id == self.default['size']][0]
            image = [i for i in self.driver.list_images() if i.id == self.default['image']][0]
            self.setting.update(image=image, size=size, ex_keyname=self.default['EC2_PRIVATE_KEY_FILE_NAME'],
                                ex_securitygroup=self.default['EC2_SECURITY_GROUP'])

        elif self.os_config.get('cm.kind') == 'openstack':
            # need someone to test it
            cls = get_driver(Provider.OPENSTACK)
            self.driver = cls(self.credentials['OS_USERNAME'],
                              self.credentials['OS_PASSWORD'],
                              ex_tenant_name=self.credentials['OS_TENANT_NAME'],
                              ex_force_auth_url=self.credentials['OS_AUTH_URL'],
                              ex_force_auth_version=self.credentials['OS_VERSION'],
                              ex_force_service_region=self.credentials['OS_REGION_NAME']
                              )
            size = [s for s in self.driver.list_sizes() if s.id == self.default['flavor']][0]
            image = [i for i in self.driver.list_images() if i.id == self.default['image']][0]
            self.setting.update(size=size, image=image)


        return self.driver

    def get_new_node_setting(self):
        """
        get the new node setting
        :return: the new node setting information
        """
        return self.setting


class Vm(object):

    def __init__(self, cloud):
        self.provider = Provider(cloud)

    def start(self, node_id):
        """
        start the node based on the id
        :param node_id:
        :return: True/False
        """
        return self.provider.ex_start_node(self.info(node_id))

    def stop(self, node_id):
        """
        stop the node based on the ide
        :param node_id:
        :return: True/False
        """
        return self.provider.ex_stop_node(self.info(node_id))

    def resume(self, node_id):
        """
        start the node based on id
        :param node_id:
        """
        self.start(node_id)

    def suspend(self, node_id):
        """
        stop the node based on id
        :param node_id:
        """
        self.stop(node_id)

    def destroy(self, node_id):
        """
        delete the node based on id
        :param node_id:
        :return: True/False
        """
        return self.provider.destroy_node(self.info(node_id))

    def create(self, name):
        """
        create a new node
        :param name: the name for the new node
        :return:
        """
        return self.provider.create_node(name=name, **self.provider.get_new_node_setting())

    def list(self):
        """
        list existed nodes
        :return: all nodes' information
        """
        return self.provider.list_nodes()

    def status(self, node_id):
        """
        show node information based on id
        :param node_id:
        :return: all information about one node
        """
        return self.info(node_id)

    def info(self, node_id):
        """
        show node information based on id
        :param node_id:
        :return: all information about one node
        """
        return self.provider.ex_get_node(node_id)
