import traceback

from datetime import datetime
from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.console import Console

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOption

from msrestazure.azure_exceptions import CloudError

class Provider(ComputeNodeABC):

    def __init__(self, name=None, configuration="~/.cloudmesh/cloudmesh4.yaml"):
        """
        Initializes the provider. The default parameters are read from the configutation
        file that is defined in yaml format.
        :param name: The name of the provider as defined in the yaml file
        :param configuration: The location of the yaml configuration file
        """

        conf = Config(configuration)["cloudmesh"]

        self.user = Config()["cloudmesh"]["profile"]["user"]

        VERBOSE("JAE "+self.user, verbose=10)

        self.spec = conf["cloud"][name]
        self.cloud = name

        cred = self.spec["credentials"]
        self.default = self.spec["default"]
        self.cloudtype = self.spec["cm"]["kind"]
        super().__init__(name, conf)

        VERBOSE(cred, verbose=10)

        if self.cloudtype != 'pyazure':
            Console.error("This class is meant for pyazure cloud")

        # ServicePrincipalCredentials related Variables to configure in cloudmesh4.yaml file
        # AZURE_APPLICATION_ID = '<Application ID from Azure Active Directory App Registration Process>'
        # AZURE_SECRET_KEY = '<Secret Key from Application configured in Azure>'
        # AZURE_TENANT_ID = '<Directory ID from Azure Active Directory section>'

        credentials = ServicePrincipalCredentials(
            client_id = cred['AZURE_APPLICATION_ID'],
            secret = cred['AZURE_SECRET_KEY'],
            tenant = cred['AZURE_TENANT_ID']
            )

        SUBSCRIPTION_ID = cred['AZURE_SUBSCRIPTION_ID']

        # Management Clients
        self.resource_client = ResourceManagementClient(credentials, SUBSCRIPTION_ID)
        self.compute_client  = ComputeManagementClient(credentials, SUBSCRIPTION_ID)
        self.network_client  = NetworkManagementClient(credentials, SUBSCRIPTION_ID)

        # Azure Resource Group
        self.GROUP_NAME      = self.default["resource_group"]

        # Azure Datacenter Region
        self.LOCATION        = cred["AZURE_REGION"]

        # NetworkManagementClient related Variables
        self.VNET_NAME       = self.default["network"]
        self.SUBNET_NAME     = self.default["subnet"]
        self.IP_CONFIG_NAME  = self.default["AZURE_VM_IP_CONFIG"]
        self.NIC_NAME        = self.default["AZURE_VM_NIC"]

        # Azure VM Storage details
        self.OS_DISK_NAME    = self.default["AZURE_VM_DISK_NAME"]
        self.USERNAME        = self.default["AZURE_VM_USER"]
        self.PASSWORD        = self.default["AZURE_VM_PASSWORD"]
        self.VM_NAME         = self.default["AZURE_VM_NAME"]

        # Create or Update Resource group
        print('\nCreate Azure Virtual Machine Resource Group')
        self.resource_client.resource_groups.create_or_update(self.GROUP_NAME, {'location': self.LOCATION})


    def create_nic(self):
        """
            Create a Network Interface for a Virtual Machine

        :return:
        """
        # Create Virtual Network
        print('\nCreate Vnet')
        async_vnet_creation = self.network_client.virtual_networks.create_or_update(
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
        print('\nCreate Subnet')
        async_subnet_creation = self.network_client.subnets.create_or_update(
            self.GROUP_NAME,
            self.VNET_NAME,
            self.SUBNET_NAME,
            {'address_prefix': '10.0.0.0/24'}
        )
        subnet_info = async_subnet_creation.result()

        # Create NIC
        print('\nCreate NIC')
        async_nic_creation = self.network_client.network_interfaces.create_or_update(
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
        self.NIC_ID = nic.id

        return nic
        # must return dict

    def start(self, groupName=None, vmName=None):
        """
        start a node

        :param name: the unique node name
        :return:  The dict representing the node
        """
        if groupName is None:
            groupName   = self.GROUP_NAME
        if vmName is None:
            vmName      = self.VM_NAME

        # Start the VM
        VERBOSE(" ".join('Starting Azure VM'))
        async_vm_start = self.compute_client.virtual_machines.start(groupName, vmName)
        async_vm_start.wait()
        return self.info(groupName)

    def restart(self, groupName=None, vmName=None):
        """
        restart a node

        :param name:
        :return: The dict representing the node
        """
        if groupName is None:
            groupName = self.GROUP_NAME
        if vmName is None:
            vmName = self.VM_NAME

        # Restart the VM
        VERBOSE(" ".join('Restarting Azure VM'))
        async_vm_restart = self.compute_client.virtual_machines.restart(groupName, vmName)
        async_vm_restart.wait()
        return self.info(groupName)

    def stop(self, groupName=None, vmName=None):
        """
        stops the node with the given name

        :param name:
        :return: The dict representing the node including updated status
        """
        if groupName is None:
            groupName = self.GROUP_NAME
        if vmName is None:
            vmName = self.VM_NAME

        # Stop the VM
        VERBOSE(" ".join('Stopping Azure VM'))
        async_vm_stop = self.compute_client.virtual_machines.power_off(groupName, vmName)
        async_vm_stop.wait()
        return self.info(groupName)

    def info(self, groupName=None):
        """
        gets the information of a node with a given name
        List VM in resource group
        :param name:
        :return: The dict representing the node including updated status
        """
        if groupName is None:
            groupName = self.GROUP_NAME

        node = self.compute_client.virtual_machines.list_all(groupName)
        return self.update_dict(node, kind="node")

    def list(self):
        """
        List all Azure Virtual Machines from my Account
        :return: dict or libcloud object
        """
        nodes = self.compute_client.virtual_machines.list_all()
        return self.update_dict(nodes, kind="node")


    # TODO Implement Suspend Method
    def suspend(self, name=None):
        """
        suspends the node with the given name

        :param name: the name of the node
        :return: The dict representing the node
        """
        raise NotImplementedError
        # must return dict

    # TODO Implement Resume Method (is it the same as restart?)
    def resume(self, name=None):
        """
        resume the named node

        :param name: the name of the node
        :return: the dict of the node
        """
        raise NotImplementedError
        # must return dict

    def destroy(self, groupName=None, vmName=None):
        """
        Destroys the node
        :param name: the name of the node
        :return: the dict of the node
        """
        if groupName is None:
            groupName = self.GROUP_NAME
        if vmName is None:
            vmName = self.VM_NAME

        # Delete VM
        VERBOSE(" ".join('Deleteing Azure Virtual Machine'))
        async_vm_delete = self.compute_client.virtual_machines.delete(groupName, vmName)
        async_vm_delete.wait()
        return self.info(groupName)

    # TODO Migrate code from Init that is meant for creating a Node
    def create(self, name=None, image=None, size=None, timeout=360, **kwargs):
        """
        creates a named node

        :param name: the name of the node
        :param image: the image used
        :param size: the size of the image
        :param timeout: a timeout in seconds that is invoked in case the image does not boot.
               The default is set to 3 minutes.
        :param kwargs: additional arguments passed along at time of boot
        :return:
        """
        """
        create one node
        """
        VM_PARAMETERS = self.create_vm_parameters()
        async_vm_creation = self.compute_client.virtual_machines.create_or_update(self.GROUP_NAME, self.VM_NAME, VM_PARAMETERS)
        async_vm_creation.wait()

        return None
        # must return dict

    # TODO Implement Rename Method
    def rename(self, name=None, destination=None):
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



    def create_vm_parameters(self):
        """
            Create the VM parameters structure.
        """
        # Parse Image1 from yaml file
        image                = self.default["image"].split(":")
        imgOS                = image[0]
        imgPublisher         = image[1]
        imgOffer             = image[2]
        imgSKU               = image[3]
        imgVersion           = image[4]

        myNic = self.network_client.network_interfaces.get(self.GROUP_NAME, self.NIC_NAME)

        print('myNicId->: '+myNic.id)

        # Declare Virtual Machine Settings

        """
            Create the VM parameters structure.
        """
        VM_PARAMETERS={
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
                imgOS: {
                    'publisher': imgPublisher,
                    'offer': imgOffer,
                    'sku': imgSKU,
                    'version': imgVersion
                },
            },
            'network_profile': {
                'network_interfaces': [{
                    'id': myNic.id,
                }]
            },
        }
        return VM_PARAMETERS

    def update_dict(self, elements, kind=None):
        """
        Libcloud returns an object or list of objects With the dict method
        this object is converted to a dict. Typically this method is used internally.
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
            entry = element.__dict__
            entry["cm"] = {
                "kind": kind,
                "driver": self.cloudtype,
                "cloud": self.cloud
            }
            if kind == 'node':
                entry["cm"]["updated"] = str(datetime.utcnow())
                entry["cm"]["name"] = entry["name"]
                entry["cm"]["region"] = entry["region"] #Check feasibility of the following items
                entry["cm"]["size"] = entry["size"] #Check feasibility of the following items
                entry["cm"]["state"] = entry["state"] #Check feasibility of the following items
                entry["cm"]["public_ips"] = entry["public_ips"] #Check feasibility of the following items
                entry["cm"]["private_ips"] = entry["private_ips"] #Check feasibility of the following items
                entry["cm"]["cloud"] = entry["cloud"] #Check feasibility of the following items
                entry["cm"]["cloud_id"] = entry["cloud_id"] #Check feasibility of the following items
                if "created_at" in entry:
                    entry["cm"]["created"] = str(entry["created_at"])
                else:
                    entry["cm"]["created"] = entry["modified"]
            elif kind == 'flavor':
                entry["cm"]["created"]  = str(datetime.utcnow())
                entry["cm"]["updated"]  = str(datetime.utcnow())
                entry["cm"]["name"]     = entry["name"]
            elif kind == 'image':
                entry['cm']['created']  = str(datetime.utcnow())
                entry['cm']['updated']  = str(datetime.utcnow())
                entry["cm"]["name"]     = entry["name"]
            elif kind == 'secgroup':
                if self.cloudtype == 'pyazure':
                    entry["cm"]["name"] = entry["name"]
                else:
                    pass

            if "extra" in entry:
                del entry["extra"]
            if "_uuid" in entry:
                del entry["_uuid"]
            if "driver" in entry:
                del entry["driver"]

            d.append(entry)
        return d
