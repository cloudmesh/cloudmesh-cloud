import time
from libcloud.compute.base import NodeAuthSSHKey
from libcloud.compute.drivers.azure_arm import AzureNetwork, AzureSubnet, AzureIPAddress, AzureNodeDriver
from libcloud.compute.base import NodeDriver
from cm4.configuration.config import Config
from cm4.vm.Cloud import Cloud


class CmAzure(Cloud):

    def __init__(self, config, cloud):
        os_config = config.get('cloud.%s' % cloud)
        default = os_config.get('default')
        credentials = os_config.get('credentials')

        self.driver = CmAzureDriver(
            tenant_id=credentials['AZURE_TENANT_ID'],
            subscription_id=credentials['AZURE_SUBSCRIPTION_ID'],
            key=credentials['AZURE_APPLICATION_ID'],
            secret=credentials['AZURE_SECRET_KEY'],
            region=default['region']
        )


class CmAzureDriver(AzureNodeDriver, NodeDriver):

    def __init__(self, tenant_id, subscription_id, key, secret,
                 secure=True, host=None, port=None,
                 api_version=None, region=None, **kwargs):

        config = Config()
        self.defaults = config.get("cloud.azure.default")
        self.resource_group = self.defaults["resource_group"]

        super().__init__(tenant_id=tenant_id,
                         subscription_id=subscription_id,
                         key=key, secret=secret,
                         secure=secure,
                         host=host, port=port,
                         api_version=api_version,
                         region=region, **kwargs)

    def stop(self, name):
        """
        Stop a running node. Deallocate resources. VM status will
        be `stopped`.
        :param name:
        """
        self.ex_stop_node(self._get_node(name))

    def suspend(self, name):
        """
        Suspend a running node. Same as `stop`, but resources do not
        deallocate. VM status will be `paused`.

        Todo: decide whether to keep this or not. Currently Vm.suspend
              doesn't pass a deallocate param.

        :param name: The name of the running node.
        """
        self.ex_stop_node(self._get_node(name), deallocate=False)

    def destroy_node(self, node):
        """
        Destroy a node.
        """
        # node = self._get_node(name)
        super().destroy_node(node)
        # Managed volumes are not destroyed by `destroy_node`.
        time.sleep(2)
        print(f"destroying volume for {node.name}")
        self.destroy_volume(self._get_volume(node.name))
        # Libcloud does not delete public IP addresses
        self._ex_delete_public_ip(f"{node.name}-ip")

    def create_node(self, name):
        """
        Create a node
        """

        # id_rsa_path = f"{Path.home()}/.ssh/id_rsa.pub"

        auth = NodeAuthSSHKey(self.defaults["public_key"])

        image = self.get_image(self.defaults["image"])
        sizes = self.list_sizes()
        size = [s for s in sizes if s.id == self.defaults["size"]][0]

        # Create a network and default subnet if none exists
        network_name = self.defaults["network"]
        network, subnet = self._create_network(network_name)

        # Create a NIC with public IP
        nic = self._create_create_nic(name, subnet)

        # Create vm
        new_vm = super().create_node(
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
        node = [n for n in self.list_nodes() if n.name == name]
        return node[0] if node else None

    def _get_volume(self, volume_id):
        """
        Get the volume named after a created node.
        """
        volume = [v for v in self.list_volumes() if v.name == volume_id]
        return volume[0] if volume else None

    def _get_network(self, network_name):
        """
        Return an instance of a network if it exists.
        """
        net = [n for n in self.ex_list_networks() if n.name == network_name]
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
        public_ip = self.ex_create_public_ip(
            f"{name}-ip",
            resource_group=self.resource_group
        )

        time.sleep(1)

        return self.ex_create_network_interface(
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
            "location": self.default_location.id,
            "properties": {
                "addressSpace": {
                    "addressPrefixes": [
                        cidr
                    ]
                }
            }
        }

        action = "/subscriptions/%s/resourceGroups/%s/providers/" \
                 "Microsoft.Network/virtualNetworks/%s" \
                 % (self.connection.subscription_id, self.resource_group, name)

        r = self.connection.request(
            action,
            params={"api-version": "2018-08-01"},
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
        action = "/subscriptions/%s/resourceGroups/%s/providers/" \
                 "Microsoft.Network/virtualNetworks/%s" \
                 % (self.connection.subscription_id, self.resource_group, name)

        r = self.connection.request(
            action,
            params={"api-version": "2018-08-01"},
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

        action = "/subscriptions/%s/resourceGroups/%s/providers/" \
                 "Microsoft.Network/virtualNetworks/%s/subnets/%s" \
                 % (self.connection.subscription_id, self.resource_group, network_name, name)

        r = self.connection.request(
            action,
            params={"api-version": "2018-08-01"},
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

        target = "/subscriptions/%s/resourceGroups/%s/" \
                 "providers/Microsoft.Network/publicIPAddresses/%s" \
                 % (self.connection.subscription_id, self.resource_group, name)

        data = {
            "location": self.default_location.id,
            "tags": {},
            "properties": {
                "publicIPAllocationMethod": "Dynamic"
            }
        }

        r = self.connection.request(
            target,
            params={"api-version": "2018-08-01"},
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
        action = "/subscriptions/%s/resourceGroups/%s/providers/" \
                 "Microsoft.Network/publicIPAddresses/%s" \
                 % (self.connection.subscription_id, self.resource_group, name)

        r = self.connection.request(
            action,
            params={"api-version": "2018-08-01"},
            method="DELETE"
        )

        return r