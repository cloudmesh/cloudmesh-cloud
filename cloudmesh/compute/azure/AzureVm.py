import time
from libcloud.compute.drivers.azure_arm import AzureNetwork, AzureSubnet, AzureIPAddress
from libcloud.compute.base import NodeAuthSSHKey
from cloudmesh.management.configuration.config import Config
from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider as LibCloudProvider


#
# TODO: possibly replace get names, images, as teher may be many images matching,
# we should assume they are in db with download, or could sheck if they do not exists so we load them.
#

class AzureProvider(object):

    def __init__(self, cloud):
        """
        Initialize the provider for the yaml file
        """
        config = Config()
        cred = config.get("cloud.azure.credentials")

        self.defaults = config.get("cloud.azure.default")
        self.resource_group = self.defaults["resource_group"]
        self.subscription_id = cred["AZURE_TENANT_ID"]

        cls = get_driver(LibCloudProvider.AZURE_ARM)
        self.api_version = {"api-version": "2018-08-01"}

        self.provider = cls(
            tenant_id=cred["AZURE_TENANT_ID"],
            subscription_id=cred["AZURE_SUBSCRIPTION_ID"],
            key=cred["AZURE_APPLICATION_ID"],
            secret=cred["AZURE_SECRET_KEY"],
            region=cred["AZURE_REGION"]
        )


    def suspend(self, name):
        """
        Suspend a running node.

        :param name: The name of the running node.
        """
        self.provider.ex_stop_node(self._get_node(name), deallocate=False)

    def destroy(self, name):
        """
        Destroy a node.
        """
        node = self._get_node(name)
        self.provider.destroy_node(node, )
        # Managed volumes are not destroyed by `destroy_node`.
        time.sleep(2)
        self.provider.destroy_volume(self._get_volume(name))
        # Libcloud does not delete public IP addresses
        self._ex_delete_public_ip(f"{name}-ip")

    def create(self, name, image_name=None, size=None):
        """
        Create a node
        """

        # id_rsa_path = f"{Path.home()}/.ssh/id_rsa.pub"

        auth = NodeAuthSSHKey(self.defaults["public_key"])

        # TODO: must be parameter
        if image_name is None:
            image_name = self.defaults["image"]

        image = self.provider.get_image(image_name)

        # TODO_ must be parameter

        if size is None:
            #
            # TODO: can this be done with get, e.g. get_size seems not to exist though
            #
            sizes = self.provider.list_sizes()
            size = [s for s in sizes if s.id == self.defaults["size"]][0]

        # Create a network and default subnet if none exists
        network_name = self.defaults["network"]
        network, subnet = self._create_network(network_name)

        # Create a NIC with public IP
        nic = self._create_create_nic(name, subnet)

        # Create vm
        new_vm = self.provider.create_node(
            name=name,
            size=size,
            image=image,
            auth=auth,
            ex_use_managed_disks=True,
            ex_resource_group=self.defaults["resource_group"],
            ex_storage_account=self.defaults["storage_account"],
            ex_nic=nic,
            ex_network=network_name
        )

        return new_vm

    def _get_node(self, name):
        """
        Get an instance of a Node returned by `list` by node name.
        """
        node = [n for n in self.list() if n.name == name]
        return node[0] if node else None

    def _get_volume(self, volume_id):
        """
        Get the volume named after a created node.
        """
        volume = [v for v in self.provider.list_volumes() if v.name == volume_id]
        return volume[0] if volume else None

    def _get_network(self, network_name):
        """
        Return an instance of a network if it exists.
        """
        net = [n for n in self.provider.ex_list_networks() if n.name == network_name]
        return net[0] if net else None

    def _create_network(self, network_name):
        """
        Create a new network resource if it does not exist or returns
        an existing network resource if it exists.
        """
        network_cidr = "10.0.0.0/16"
        network = self._ex_create_network(name=network_name, cidr=network_cidr)
        time.sleep(2)
        subnet_name = "default"
        subnet_cidr = "10.0.0.0/16"
        subnet = self._ex_create_subnet(name=subnet_name, cidr=subnet_cidr, network_name=network_name)
        time.sleep(2)
        return network, subnet

    def _create_create_nic(self, name, subnet):
        """
        Create a network interface card with a public IP
        :param name: The name of the node
        :param subnet: The `AzureSubnet` where the nic will reside
        :return:
        """
        public_ip = self.provider.ex_create_public_ip(
            f"{name}-ip",
            resource_group=self.resource_group
        )

        time.sleep(1)

        return self.provider.ex_create_network_interface(
            name=f"{name}-nic",
            subnet=subnet,
            resource_group=self.resource_group,
            public_ip=public_ip
        )

    def _ex_create_network(self, cidr, name):
        """
        Create a network
        """
        data = {
            "location": self.provider.default_location.id,
            "properties": {
                "addressSpace": {
                    "addressPrefixes": [
                        cidr
                    ]
                }
            }
        }

        subscription = self.provider.connection.subscription_id
        resource_group = self.resource_group

        action = f"/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/" \
            "Microsoft.Network/virtualNetworks/{name}"

        r = self.provider.connection.request(
            action,
            params=self.api_version,
            method="PUT",
            data=data
        )

        return AzureNetwork(
            id=r.object["id"],
            name=r.object["name"],
            location=r.object["location"],
            extra=r.object["properties"]
        )

    def _ex_delete_network(self, name):
        """
        Delete a network
        """

        subscription = self.provider.connection.subscription_id
        resource_group = self.resource_group

        action = f"/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/" \
            "Microsoft.Network/virtualNetworks/{name}"

        r = self.provider.connection.request(
            action,
            params=self.api_version,
            method="DELETE"
        )

        return r

    def _ex_create_subnet(self, cidr, network_name, name):
        """
        Create a subnet
        """
        data = {
            "properties": {
                "addressPrefix": cidr
            }
        }

        subscription = self.provider.connection.subscription_id
        resource_group = self.resource_group

        action = "/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/" \
                 "Microsoft.Network/virtualNetworks/{network_name}/subnets/{name}"

        r = self.provider.connection.request(
            action,
            params=self.api_version,
            method="PUT",
            data=data
        )

        return AzureSubnet(
            id=r.object["id"],
            name=r.object["name"],
            extra=r.object["properties"]
        )

    def _ex_create_public_ip(self, name):
        """
        Create a public IP resources.
        """

        subscription = self.provider.connection.subscription_id
        resource_group = self.resource_group

        target = "/subscriptions/{subscription}/resourceGroups/{resource_gropu}/" \
                 "providers/Microsoft.Network/publicIPAddresses/name"

        data = {
            "location": self.provider.default_location.id,
            "tags": {},
            "properties": {
                "publicIPAllocationMethod": "Dynamic"
            }
        }

        r = self.connection.request(
            target,
            params=self.api_version,
            data=data,
            method='PUT'
        )

        return AzureIPAddress(
            id=r.object["id"],
            name=r.object["name"],
            extra=r.object["properties"]
        )

    def _ex_delete_public_ip(self, name):
        """
        Delete a public IP
        :param name:
        :return:
        """

        subscription = self.provider.connection.subscription_id
        resource_group = self.resource_group

        action = "/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/" \
                 "Microsoft.Network/publicIPAddresses/{name}"

        r = self.provider.connection.request(
            action,
            params=self.api_version,
            method="DELETE"
        )

        return r
