from ast import literal_eval
from datetime import datetime
from pprint import pprint

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.management.configuration.config import Config


class Provider(ComputeNodeABC):
    kind = 'azure'

    """
    output = {
        "image": {
            "sort_keys": ["cm.name",
                          "extra.minDisk"],
            "order": ["image.id",
                      "image.name",
                      "image.type",
                      "image.location",
                      "hardware_profile.vm_size",
                      "image_reference.publisher",
                      "image_reference.offer",
                      "image_reference.sku",
                      "image_reference.version"],
            "header": ["Id",
                       "Name",
                       "TYpe",
                    ]
            },
        "vm": {},
        "flavor": {},
        "status": {},
        "key":{},
        "secgroup": {},
        "secrule": {},
    }
    """

    """      
                     
        "os_disk": {
            "os_type": [],
            "name": [],
            "caching": [],
            "create_option": [],
            "disk_size_gb": [],
            "managed_disk": ["id",
                             "storage_account_type"]
        },
        "data_disks": {
            "lun": [],
            "name": [],
            "caching": [],
            "create_option": [],
            "disk_size_gb": [],
            "managed_disk": ["id",
                             "storage_account_type"]
        },
        "os_profile": {
            "computer_name": [],
            "admin_username": [],
            "linux_configuration": ["disable_password_authentication",
                                    "provision_vm_agent"],
            "secrets": [],
            "allow_extension_operations": []
        },
        "network_profile": {
            "network_interfaces": ["id"]
        },
        "provisioning_state": [],
        "vm_id": []
    
        }
        }
    """

    # noinspection PyPep8Naming

    def Print(self, output, kind, data):
        # TODO: Moeen
        raise NotImplementedError

    def find(self, elements, name=None):
        # TODO: Moeen
        raise NotImplementedError

    def keys(self):
        # TODO: Moeen
        raise NotImplementedError

    def key_upload(self, key=None):
        # TODO: Moeen
        raise NotImplementedError

    def key_delete(self, name=None):
        # TODO: Moeen
        raise NotImplementedError

    def list_secgroups(self, name=None):
        raise NotImplementedError

    def list_secgroup_rules(self, name='default'):
        raise NotImplementedError

    def add_secgroup(self, name=None, description=None):
        raise NotImplementedError

    def add_secgroup_rule(self,
                          name=None,  # group name
                          port=None,
                          protocol=None,
                          ip_range=None):
        raise NotImplementedError

    def remove_secgroup(self, name=None):
        raise NotImplementedError

    def upload_secgroup(self, name=None):
        raise NotImplementedError

    def add_rules_to_secgroup(self, name=None, rules=None):
        raise NotImplementedError

    def remove_rules_from_secgroup(self, name=None, rules=None):
        raise NotImplementedError

    def flavor(self, name=None):
        # TODO: Joaquin
        raise NotImplementedError

    def set_server_metadata(self, name, m):
        # TODO: Joaquin
        raise NotImplementedError

    def get_server_metadata(self, name):
        # TODO: Joaquin
        raise NotImplementedError

    def delete_server_metadata(self, name, key):
        # TODO: Joaquin
        raise NotImplementedError

    # these are available to be associated
    def list_public_ips(self,
                        ip=None,
                        available=False):
        # TODO: Moeen
        raise NotImplementedError

    # release the ip
    def delete_public_ip(self, ip=None):
        # TODO: Moeen
        raise NotImplementedError

    def create_public_ip(self):
        # TODO: Moeen
        raise NotImplementedError

    def find_available_public_ip(self):
        # TODO: Moeen
        raise NotImplementedError

    def attach_public_ip(self, node, ip):
        # TODO: Moeen
        raise NotImplementedError

    def detach_public_ip(self, node, ip):
        # TODO: Moeen
        raise NotImplementedError

    # see the openstack example it will be almost the same as in openstack
    # other than getting
    # the ip and username
    def ssh(self, vm=None, command=None):
        raise NotImplementedError

    # noinspection PyPep8Naming
    def __init__(self, name=None, configuration="~/.cloudmesh/cloudmesh4.yaml"):
        """
        Initializes the provider. The default parameters are read from the
        configuration file that is defined in yaml format.

        :param name: The name of the provider as defined in the yaml file
        :param configuration: The location of the yaml configuration file
        """

        conf = Config(configuration)["cloudmesh"]

        self.user = Config()["cloudmesh"]["profile"]["user"]

        self.spec = conf["cloud"][name]
        self.cloud = name

        cred = self.spec["credentials"]
        self.default = self.spec["default"]
        self.cloudtype = self.spec["cm"]["kind"]
        super().__init__(name, conf)

        VERBOSE(cred, verbose=10)

        if self.cloudtype != 'azure':
            Console.error("This class is meant for azure cloud")

        # ServicePrincipalCredentials related Variables to configure in
        # cloudmesh4.yaml file

        # AZURE_APPLICATION_ID = '<Application ID from Azure Active Directory
        # App Registration Process>'

        # AZURE_SECRET_KEY = '<Secret Key from Application configured in
        # Azure>'

        # AZURE_TENANT_ID = '<Directory ID from Azure Active Directory
        # section>'

        credentials = ServicePrincipalCredentials(
            client_id=cred['AZURE_APPLICATION_ID'],
            secret=cred['AZURE_SECRET_KEY'],
            tenant=cred['AZURE_TENANT_ID']
        )

        subscription = cred['AZURE_SUBSCRIPTION_ID']

        # Management Clients
        self.resource_client = ResourceManagementClient(
            credentials, subscription)
        self.compute_client = ComputeManagementClient(
            credentials, subscription)
        self.network_client = NetworkManagementClient(
            credentials, subscription)

        # VMs abbreviation
        self.vms = self.compute_client.virtual_machines
        self.imgs = self.compute_client.virtual_machine_images

        # Azure Resource Group
        self.GROUP_NAME = self.default["resource_group"]

        # Azure Datacenter Region
        self.LOCATION = cred["AZURE_REGION"]

        # NetworkManagementClient related Variables
        self.VNET_NAME = self.default["network"]
        self.SUBNET_NAME = self.default["subnet"]
        self.IP_CONFIG_NAME = self.default["AZURE_VM_IP_CONFIG"]
        self.NIC_NAME = self.default["AZURE_VM_NIC"]

        # Azure VM Storage details
        self.OS_DISK_NAME = self.default["AZURE_VM_DISK_NAME"]
        self.USERNAME = self.default["AZURE_VM_USER"]
        self.PASSWORD = self.default["AZURE_VM_PASSWORD"]
        self.VM_NAME = self.default["AZURE_VM_NAME"]

        # Create or Update Resource group
        self.get_resource_group()

    def get_resource_group(self):
        groups = self.resource_client.resource_groups
        if groups.check_existence(self.GROUP_NAME):
            return groups.get(self.GROUP_NAME)
        else:
            # Create or Update Resource group
            VERBOSE(" ".join('Create Azure Virtual Machine Resource Group'))
            return groups.create_or_update(
                self.GROUP_NAME, {'location': self.LOCATION})

    def create(self, name=None,
               image=None,
               size=None,
               location=None,
               timeout=180,
               key=None,
               secgroup=None,
               ip=None,
               user=None,
               public=True,
               group=None,
               metadata=None,
               **kwargs):
        """
        creates a named node

        :param name: the name of the node
        :param image: the image used
        :param size: the size of the image
        :param timeout: a timeout in seconds that is invoked in case the image
                        does not boot. The default is set to 3 minutes.
        :param kwargs: additional arguments passed along at time of boot
        :return:
        """

        vm_parameters = self.create_vm_parameters()

        async_vm_creation = self.vms.create_or_update(
            self.GROUP_NAME,
            self.VM_NAME,
            vm_parameters)
        async_vm_creation.wait()

        # Creating a Managed Data Disk
        async_disk_creation = self.compute_client.disks.create_or_update(
            self.GROUP_NAME,
            'cloudmesh-datadisk1',
            {
                'location': self.LOCATION,
                'disk_size_gb': 1,
                'creation_data': {
                    'create_option': 'Empty'
                }
            }
        )
        data_disk = async_disk_creation.result()

        # Get the virtual machine by name
        virtual_machine = self.vms.get(
            self.GROUP_NAME,
            self.VM_NAME
        )

        # Attaching Data Disk to a Virtual Machine
        virtual_machine.storage_profile.data_disks.append({
            'lun': 12,
            'name': 'cloudmesh-datadisk1',
            'create_option': 'Attach',
            'managed_disk': {
                'id': data_disk.id
            }
        })
        async_disk_attach = self.vms.create_or_update(
            self.GROUP_NAME,
            virtual_machine.name,
            virtual_machine
        )
        async_disk_attach.wait()

        return self.info(self.GROUP_NAME, self.VM_NAME)

    def create_vm_parameters(self):
        nic = self.create_nic()

        # Parse Image from yaml file

        publisher, offer, sku, version = self.default["image"].split(":")

        # Declare Virtual Machine Settings

        """
            Create the VM parameters structure.
        """
        vm_parameters = {
            'location': self.LOCATION,
            'os_profile': {
                'computer_name': self.VM_NAME,
                'admin_username': self.USERNAME,
                'admin_password': self.PASSWORD
            },
            'hardware_profile': {
                'vm_size': 'Standard_DS1_v2'
            },
            'storage_profile': {
                'image_reference': {
                    'publisher': publisher,
                    'offer': offer,
                    'sku': sku,
                    'version': version
                },
            },
            'network_profile': {
                'network_interfaces': [{
                    'id': nic.id,
                }]
            },
        }

        return vm_parameters

    def create_nic(self):
        """
            Create a Network Interface for a Virtual Machine
        :return:
        """
        # A Resource group needs to be in place
        self.get_resource_group()

        # Create Virtual Network
        VERBOSE(" ".join('Create Vnet'))
        async_vnet_creation = \
            self.network_client.virtual_networks.create_or_update(
                self.GROUP_NAME,
                self.VNET_NAME,
                {
                    'location': self.LOCATION,
                    'address_space': {
                        'address_prefixes': ['10.0.0.0/16']
                    }
                }
            )
        async_vnet_creation.wait()

        # Create Subnet
        VERBOSE(" ".join('Create Subnet'))
        async_subnet_creation = self.network_client.subnets.create_or_update(
            self.GROUP_NAME,
            self.VNET_NAME,
            self.SUBNET_NAME,
            {'address_prefix': '10.0.0.0/24'}
        )
        subnet_info = async_subnet_creation.result()

        # Create NIC
        VERBOSE(" ".join('Create NIC'))
        async_nic_creation = \
            self.network_client.network_interfaces.create_or_update(
                self.GROUP_NAME,
                self.NIC_NAME,
                {
                    'location': self.LOCATION,
                    'ip_configurations': [{
                        'name': self.IP_CONFIG_NAME,
                        'subnet': {
                            'id': subnet_info.id
                        }
                    }]
                }
            )

        nic = async_nic_creation.result()

        return nic

    def start(self, group=None, name=None):
        """
        start a node

        :param group: the unique Resource Group name
        :param name: the unique Virtual Machine name
        :return:  The dict representing the node
        """
        if group is None:
            group = self.GROUP_NAME
        if name is None:
            name = self.VM_NAME

        # Start the VM
        VERBOSE(" ".join('Starting Azure VM'))
        async_vm_start = self.vms.start(group, name)
        async_vm_start.wait()
        return self.info(group, name)

    def reboot(self, group=None, name=None):
        """
        restart/reboot a node

        :param group: the unique Resource Group name
        :param name: the unique Virtual Machine name
        :return: The dict representing the node
        """
        if group is None:
            group = self.GROUP_NAME
        if name is None:
            name = self.VM_NAME

        # Restart the VM
        VERBOSE(" ".join('Restarting Azure VM'))
        async_vm_restart = self.vms.restart(group, name)
        async_vm_restart.wait()
        return self.info(group, name)

    def stop(self, group=None, name=None):
        """
        stops the node with the given name

        :param group: the unique Resource Group name
        :param name: the unique Virtual Machine name
        :return: The dict representing the node including updated status
        """
        if group is None:
            group = self.GROUP_NAME
        if name is None:
            name = self.VM_NAME

        # Stop the VM
        VERBOSE(" ".join('Stopping Azure VM'))
        async_vm_stop = self.vms.power_off(group, name)
        async_vm_stop.wait()
        return self.info(group, name)

    def resume(self, group=None, name=None):
        """
        resume the named node since Azure does not handle resume it uses start

        :param group: the unique Resource Group name
        :param name: the unique Virtual Machine name
        :return: The dict representing the node including updated status
        """
        if group is None:
            group = self.GROUP_NAME
        if name is None:
            name = self.VM_NAME

        return self.start(group, name)

    def suspend(self, group=None, name=None):
        """
        suspends the node with the given name since Azure does not handle suspend it uses stop

        :param group: the unique Resource Group name
        :param name: the unique Virtual Machine name
        :return: The dict representing the node including updated status
        """
        if group is None:
            group = self.GROUP_NAME
        if name is None:
            name = self.VM_NAME

        return self.stop(group, name)

    def info(self, group=None, name=None):
        """
        gets the information of a node with a given name
        List VM in resource group
        :param group: the unique Resource Group name
        :param name: the unique Virtual Machine name
        :return: The dict representing the node including updated status
        """
        if group is None:
            group = self.GROUP_NAME

        if name is None:
            name = self.VM_NAME

        node = self.vms.get(group, name)

        return node

    def list(self):
        """
        List all Azure Virtual Machines from my Account
        :return: dict or libcloud object
        """
        servers = self.vms.list_all()

        result = []
        for server in servers:

            if 'cm' in server['metadata']:
                metadata = server['metadata']['cm']
                cm = literal_eval(metadata)
                if 'cm' in server:
                    server['cm'].update(cm)
            result.append(server)

        return result

    def destroy(self, group=None, name=None):
        """
        Destroys the node
        :param name: the name of the node
        :return: the dict of the node
        """
        if group is None:
            group = self.GROUP_NAME
        if name is None:
            name = self.VM_NAME

        # Delete VM
        VERBOSE(" ".join('Deleting Azure Virtual Machine'))
        async_vm_delete = self.vms.delete(group, name)
        async_vm_delete.wait()

        # Delete Resource Group
        VERBOSE(" ".join('Deleting Azure Resource Group'))
        async_group_delete = self.resource_client.resource_groups.delete(
            group)
        async_group_delete.wait()

        # return self.info(groupName)
        return None

    def images(self, **kwargs):
        """
        Lists the images on the cloud
        :return: dict or libcloud object
        """
        region = self.LOCATION

        image_list = list()

        result_list_pub = self.imgs.list_publishers(
            region,
        )

        for publisher in result_list_pub:
            try:
                result_list_offers = self.imgs.list_offers(
                    region,
                    publisher.name,
                )

                for offer in result_list_offers:
                    try:
                        result_list_skus = self.imgs.list_skus(
                            region,
                            publisher.name,
                            offer.name,
                        )

                        for sku in result_list_skus:
                            try:
                                result_list = self.imgs.list(
                                    region,
                                    publisher.name,
                                    offer.name,
                                    sku.name,
                                )

                                for version in result_list:
                                    try:
                                        result_get = self.imgs.get(
                                            region,
                                            publisher.name,
                                            offer.name,
                                            sku.name,
                                            version.name,
                                        )

                                        msg = 'PUBLISHER: {0}, OFFER: {1}, SKU: {2}, VERSION: {3}'.format(
                                            publisher.name,
                                            offer.name,
                                            sku.name,
                                            version.name,
                                        )
                                        VERBOSE(msg)
                                        image_list.append(result_get)
                                    except:
                                        print("Something failed in result_list")

                            except:
                                print("Something failed in result_list_skus")

                    except:
                        print("Something failed in result_list_offers")

            except:
                print("Something failed in result_list_pub")

        return self.get_list(image_list, kind="image")

    def image(self, name=None):
        """
        Gets the image with a given nmae
        :param name: The name of the image
        :return: the dict of the image
        """
        return self.find(self.images(**kwargs), name=name)

    def get_list(self, d, kind=None, debug=False, **kwargs):
        """
        Lists the dict d on the cloud
        :return: dict or libcloud object
        """

        if self.vms:
            entries = []
            for entry in d:
                entries.append(dict(entry))
            if debug:
                pprint(entries)

            return self.update_dict(entries, kind=kind)
        return None

    # TODO Implement Rename Method
    def rename(self, name=None, destination=None):
        # TODO: Moeen
        """
        rename a node

        :param destination:
        :param name: the current name
        :return: the dict with the new name
        """
        # if destination is None, increase the name counter and use the new name
        # must return dict

        HEADING(c=".")
        return None

    def update_dict(self, elements, kind=None):
        """
        Libcloud returns an object or list of objects With the dict method
        this object is converted to a dict. Typically this method is used
        internally.

        :param elements: the elements
        :param kind: Kind is image, flavor, or node, secgroup and key
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
            entry = element
            entry["cm"] = {
                "kind": kind,
                "driver": self.cloudtype,
                "cloud": self.cloud
            }
            if kind == 'vm':
                entry["cm"]["updated"] = str(datetime.utcnow())
                entry["cm"]["name"] = entry["name"]
                entry["cm"]["type"] = entry[
                    "type"]  # Check feasibility of the following items
                entry["cm"]["location"] = entry[
                    "location"]  # Check feasibility of the following items
            elif kind == 'flavor':
                entry["cm"]["created"] = str(datetime.utcnow())
                entry["cm"]["updated"] = str(datetime.utcnow())
                entry["cm"]["name"] = entry["name"]
            elif kind == 'image':
                entry['cm']['created'] = str(datetime.utcnow())
                entry['cm']['updated'] = str(datetime.utcnow())
                entry["cm"]["name"] = entry["name"]
            elif kind == 'secgroup':
                if self.cloudtype == 'azure':
                    entry["cm"]["name"] = entry["name"]
                else:
                    pass

            d.append(entry)
            VERBOSE(d)

        return d
