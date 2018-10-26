from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.base import NodeAuthSSHKey
from cm4.abstractclass.CloudManagerABC import CloudManagerABC
from cm4.configuration.config import Config


class AzureManager(CloudManagerABC):

    def __init__(self):
        """
        Initialize AzureManager

        TODO: Factor out need for network and storage resources
        """
        config = Config()
        cred = config.get('cloud.azure.credentials')
        self.defaults = config.get('cloud.azure.default')

        cls = get_driver(Provider.AZURE_ARM)
        self.conn = cls(
            tenant_id=cred['AZURE_TENANT_ID'],
            subscription_id=cred['AZURE_SUBSCRIPTION_ID'],
            key=cred['AZURE_APPLICATION_ID'],
            secret=cred['AZURE_SECRET_KEY'],
            region=self.defaults['region']
        )

    def suspend(self, name):
        """
        Suspend a running node.

        :param name: The name of the running node.
        """
        self.conn.ex_stop_node(self._get_node(name), deallocate=False)

    def resume(self, name):
        """
        Start a suspended node.

        :param name: The name of the suspended node.
        """
        self.start(name)

    def start(self, name):
        """
        Start a stopped node.

        :param name: The name of the stopped node.
        """
        self.conn.ex_start_node(self._get_node(name))

    def stop(self, name):
        """
        Stop a running node.

        :param name: The name of the running node.
        """
        self.conn.ex_stop_node(self._get_node(name))

    def ls(self):
        """
        List all nodes.
        """
        return self.conn.list_nodes()

    def info(self, id):
        """
        Get all information about one node.
        """
        return self.conn.ex_get_node(id)

    def _get_node(self, name):
        """
        Get an instance of a Node returned by `ls` by node name.
        TODO: Compare with results of `info`. weigh lookup by `id` vs `name`. ID will be better when DB is implimented
        """
        node = [n for n in self.ls() if n.name == name]
        return node[0] if node else None

    def destroy(self, name):
        """
        Destroy a node.
        """
        self.conn.destroy_node(self._get_node(name))

    def create(self, name):
        """
        Create a node

        TODO: Create NIC so that a network doesn't have to be configured beforehand.
        TODO: Add public IP
        TODO: Check for parameters like auth and other defaults.
        """
        auth = NodeAuthSSHKey(self.defaults['public_key'])

        image = self.conn.get_image(self.defaults['image'])

        sizes = self.conn.list_sizes()

        size = [s for s in sizes if s.id == self.defaults['size']][0]

        new_vm = self.conn.create_node(
            name=name,
            size=size,
            image=image,
            auth=auth,
            ex_use_managed_disks=True,
            ex_resource_group=self.defaults['resource_group'],
            ex_storage_account=self.defaults['storage_account'],
            ex_network=self.defaults['network']
        )

        return new_vm
