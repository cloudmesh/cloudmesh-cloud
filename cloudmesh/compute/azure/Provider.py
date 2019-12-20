import ctypes
import os
import subprocess
from datetime import datetime
from pprint import pprint
from sys import platform

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network.v2018_12_01.models import SecurityRule
from azure.mgmt.resource import ResourceManagementClient
from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING, banner
from cloudmesh.configuration.Config import Config
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.provider import ComputeProviderPlugin
from msrestazure.azure_exceptions import CloudError

CLOUDMESH_YAML_PATH = "~/.cloudmesh/cloudmesh.yaml"


def _remove_mongo_id_obj(dict_list):
    for i in dict_list:
        try:
            i.pop('_id')
        except KeyError:
            pass

    return dict_list


def _get_az_vm_status(az_status):
    az_status = az_status.lower()
    if 'running' in az_status:
        return 'ACTIVE'
    elif 'stopped' in az_status:
        return 'STOPPED'
    else:
        return None


class Provider(ComputeNodeABC, ComputeProviderPlugin):
    """
    verbosity

    8 - prints major actions
    9 - prints all images
    10 - prints all update dicts

    """
    kind = 'azure'

    sample = """
        cloudmesh:
          cloud:
            {name}:
              cm:
                active: true
                heading: {name}
                host: TBD
                label: {name}
                kind: azure
                version: latest
                service: compute
              default:
                image: Canonical:UbuntuServer:16.04.0-LTS:latest
                size: Basic_A0
                resource_group: cloudmesh
                storage_account: cmdrive
                network: cmnetwork
                subnet: cmsubnet
                blob_container: vhds
                AZURE_VM_IP_CONFIG: cloudmesh-ip-config
                AZURE_VM_NIC: cloudmesh-nic
                AZURE_VM_DISK_NAME: cloudmesh-os-disk
                AZURE_VM_USER: TBD
                AZURE_VM_PASSWORD: TBD
                AZURE_VM_NAME: cloudmeshVM
              credentials:
                AZURE_TENANT_ID: {tenantid}
                AZURE_SUBSCRIPTION_ID: {subscriptionid}
                AZURE_APPLICATION_ID: {applicationid}
                AZURE_SECRET_KEY: {secretkey}
                AZURE_REGION: eastus
        """

    vm_state = [
        'ACTIVE',
        'BUILDING',
        'DELETED',
        'ERROR',
        'HARD_REBOOT',
        'PASSWORD',
        'PAUSED',
        'REBOOT',
        'REBUILD',
        'RESCUED',
        'RESIZED',
        'REVERT_RESIZE',
        'SHUTOFF',
        'SOFT_DELETED',
        'STOPPED',
        'SUSPENDED',
        'UNKNOWN',
        'VERIFY_RESIZE'
    ]

    output = {
        "status": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.cloud",
                      "vm_state",
                      "status",
                      "task_state"],
            "header": ["Name",
                       "Cloud",
                       "State",
                       "Status",
                       "Task"]
        },
        "vm": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.cloud",
                      "id",
                      "type",
                      "location",
                      "hardware_profile.vm_size",
                      "storage_profile.image_reference.image_reference",
                      "storage_profile.image_reference.offer",
                      "storage_profile.image_reference.sku",
                      "storage_profile.image_reference.version",
                      "storage_profile.os_disk.os_type",
                      "storage_profile.os_disk.name",
                      "storage_profile.os_disk.caching",
                      "storage_profile.os_disk.create_option",
                      "storage_profile.os_disk.disk_size_gb",
                      "storage_profile.os_disk.managed_disk.id",
                      "storage_profile.os_disk.managed_disk.storage_account_type",
                      "storage_profile.data_disks.lun",
                      "storage_profile.data_disks.name",
                      "storage_profile.data_disks.caching",
                      "storage_profile.data_disks.create_option",
                      "storage_profile.data_disks.disk_size_gb",
                      "storage_profile.data_disks.managed_disk.id",
                      "storage_profile.data_disks.managed_disk.storage_account_type",
                      "os_profile.computer_name",
                      "os_profile.admin_username",
                      "os_profile.linux_configuration.disable_password_authentication",
                      "os_profile.linux_configuration.provision_vm_agent",
                      "os_profile.allow_extension_operations",
                      "network_profile.network_interfaces.id",
                      "provisioning_state",
                      "vm_id",
                      "cm.kind"],
            "header": ["Name",
                       "Cloud",
                       "Id",
                       "Type",
                       "Location",
                       "VM_Size",
                       "Image Reference",
                       "Image Offer",
                       "Image Sku",
                       "Image Version",
                       "Image OS Type",
                       "Image OS Disk Name",
                       "Image OS Disk Caching",
                       "Image OS Disk Create Option",
                       "Image OS Disk Size",
                       "Image OS Disk ID",
                       "Image OS Disk Storage Type",
                       "Image Data Disk Lun",
                       "Image Data Disk Name",
                       "Image Data Disk Caching",
                       "Image Data Disk Create Option",
                       "Image Data Disk Size",
                       "Image Data Disk Id",
                       "Image Data Disk Storage Type",
                       "Image Os Profile Computer Name",
                       "Image Os Profile Admin Username",
                       "Image Linux Conf Disable Password",
                       "Image Linux Conf Provision VM Agent",
                       "Image Os Profile Allow Extension Operations",
                       "Network Interfaces ID",
                       "Provisioning State",
                       "VM ID",
                       "Kind"]
        },
        "image": {
            "sort_keys": ["cm.name",
                          "plan.publisher"],
            "order": ["cm.name",
                      "location",
                      "plan.publisher",
                      "plan.name",
                      "plan.product",
                      "operating_system"],
            "header": ["Name",
                       "Location",
                       "Publisher",
                       "Plan Name",
                       "Product",
                       "Operating System",
                       ]
        },
        "flavor": {
            "sort_keys": ["name",
                          "number_of_cores",
                          "os_disk_size_in_mb"],
            "order": ["name",
                      "number_of_cores",
                      "os_disk_size_in_mb",
                      "resource_disk_size_in_mb",
                      "memory_in_mb",
                      "max_data_disk_count"],
            "header": ["Name",
                       "NumberOfCores",
                       "OS_Disk_Size",
                       "Resource_Disk_Size",
                       "Memory",
                       "Max_Data_Disk"]},
        # "status": {},
        "key": {},  # Moeen
        "secgroup": {},  # Moeen
        "secrule": {},  # Moeen
    }

    # noinspection PyPep8Naming
    def __init__(self, name="azure", configuration=None, credentials=None):
        """
        Initializes the provider. The default parameters are read from the
        configuration file that is defined in yaml format.

        :param name: The name of the provider as defined in the yaml file
        :param configuration: The location of the yaml configuration file
        """
        configuration = configuration if configuration is not None \
            else CLOUDMESH_YAML_PATH

        conf = Config(configuration)["cloudmesh"]

        self.user = Config()["cloudmesh"]["profile"]["user"]

        self.spec = conf["cloud"][name]
        self.cloud = name

        cred = self.spec["credentials"]
        self.default = self.spec["default"]
        self.cloudtype = self.spec["cm"]["kind"]
        super().__init__(name, configuration)

        # update credentials with the passed dict
        if credentials is not None:
            cred.update(credentials)

        VERBOSE(cred, verbose=10)

        if self.cloudtype != 'azure':
            Console.error("This class is meant for azure cloud")

        # ServicePrincipalCredentials related Variables to configure in
        # cloudmesh.yaml file

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

        # Azure VM Storage details
        self.OS_DISK_NAME = self.default["AZURE_VM_DISK_NAME"]
        self.USERNAME = self.default["AZURE_VM_USER"]
        self.PASSWORD = self.default["AZURE_VM_PASSWORD"]
        self.VM_NAME = self.default["AZURE_VM_NAME"]
        self.NIC_NAME = self.default["AZURE_VM_NIC"]

        # public IPs
        self.PUBLIC_IP__NAME = self.VM_NAME + '-pub-ip'

        # Create or Update Resource group
        self._get_resource_group()

        self.cmDatabase = CmDatabase()

        self.protocol_str_map = {
            'tcp': 'Tcp',
            'udp': 'Udp',
            'icmp': 'Icmp',
            'esp': 'Esp',
            'ah': 'Ah',
            '*': '*'
        }

    def Print(self, data, output=None, kind=None):
        if output == "table":
            if kind == "secrule":

                result = []
                for group in data:
                    for rule in group['security_group_rules']:
                        rule['name'] = group['name']
                        result.append(rule)
                data = result

            order = self.output[kind]['order']  # not pretty
            header = self.output[kind]['header']  # not pretty
            humanize = self.output[kind]['humanize']  # not pretty

            print(Printer.flatwrite(data,
                                    sort_keys=["name"],
                                    order=order,
                                    header=header,
                                    output=output,
                                    humanize=humanize)
                  )
        else:
            print(Printer.write(data, output=output))

    # noinspection PyPep8Naming

    #    def Print(self, output, kind, data):
    # TODO: Moeen
    #        raise NotImplementedError

    def keys(self):
        """
        The keys command in Azure is not supported

        TODO: BUG: therefore it should just return the keys form the local db to
                   make it appear it is supported. So instead do get the output,
                   see how it is implemented in key list

        :return:
        """
        Console.error("Key list is not supported in Azure!")
        Console.msg("Please use ")
        Console.msg("")
        Console.msg("    cms key list ")
        Console.msg("")
        return None

    def key_upload(self, key=None):
        """
        TODO: implement alternative

        azure does not allow explicit key upload!


        :param key:
        :return:
        """
        Console.error(f'Azure does not allow explicit key upload! '
                      f'Please use \'cms key\' operations to add keys to the '
                      f'local db and reference them at the VM creation!')

        return None

    def key_delete(self, name=None):
        """
        TODO: implement alternative

                azure does not allow explicit key upload!


        :param name:
        :return:
        """
        Console.error(f"Azure does not allow explicit key delete! "
                      f"Please use 'cms key' operations to delete keys from "
                      f"the local db!")
        return None

    def _get_az_public_ip(self, ip_name):
        ip = next((x for x in self.list_public_ips() if
                   x['name'] == ip_name), None)
        return ip

    def get_public_ip(self, name=None):
        """
        returns public IP by vm name from the Az public IPs

        :param name:
        :return:
        """
        _, pub_ip = self._get_pub_ip_for_vm(name)
        return pub_ip['ip_address']

    # these are available to be associated
    def list_public_ips(self, ip=None, available=False):
        """
        lists public ips of the group

        :param ip:
        :param available:
        :return:
        """
        list_result = [i.__dict__ for i in
                       self.network_client.public_ip_addresses.list(
                           self.GROUP_NAME)]

        return self.update_dict(list_result, kind='ip')

    def delete_public_ip(self, ip=None):
        """
        deletes public ip by name

        :param ip:
        :return:
        """
        if ip is not None:
            res = self.network_client.public_ip_addresses.delete(
                self.GROUP_NAME,
                ip
            )
            res.wait()

            Console.info(f'{ip} was deleted!')
        else:
            Console.warning('No ip was provided')

    def create_public_ip(self):
        """
        Creates public IP for the group using the ip name provided in the config
        as a prefix

        :return:
        """
        current_pub_count = len(self.list_public_ips())

        public_ip_params = {
            'location': self.LOCATION,
            'sku': {
                'name': 'Basic',
            }
        }

        creation_result = self.network_client.public_ip_addresses. \
            create_or_update(self.GROUP_NAME,
                             f"{self.PUBLIC_IP__NAME}_{current_pub_count}",
                             public_ip_params,
                             ).result()
        Console.info("Public IP created: " + creation_result.name)
        return self.update_dict([creation_result.as_dict()], kind='ip')

    def find_available_public_ip(self):
        """
        Azure currenly has no direct API to check if an IP is available or not!
        hence create an IP everytime this method is called!

        :return:
        """
        # pub_ips = self.list_public_ips()
        #
        # for ip in pub_ips:
        #     if ip['ip_configuration'] is None:
        #         # if ip_configuration is none -> ip is available
        #         # --> return it!
        #         Console.info(f"Found available ip {ip['name']}")
        #         return ip

        # if not len(pub_ips) == 0 create one
        Console.info(f"Creating new public IP")
        return self.create_public_ip()

    def attach_public_ip(self, node=None, ip=None):
        """
        attaches a public ip to a node

        :param node:
        :param ip:
        :return:
        """
        ip = self.find_available_public_ip()[0].as_dict()

        # remove cm dict
        ip.pop('cm')

        # to attach a public ip, get the nic and update the public ip field via
        # IP config
        ip_config = self.network_client.network_interface_ip_configurations.get(
            self.GROUP_NAME, self.NIC_NAME, self.IP_CONFIG_NAME
        )

        ip_config.public_ip_address = ip

        res = self.network_client.network_interfaces.create_or_update(
            self.GROUP_NAME,
            self.NIC_NAME,
            parameters={
                'location': self.LOCATION,
                'ip_configurations': [ip_config.as_dict()]
            }
        )

        return res.result()

    def detach_public_ip(self, node=None, ip=None):
        """
        TBD

        :param node:
        :param ip:
        :return:
        """
        if ip is None:
            vm_obj = self._get_local_vm(node)
            nic_id = vm_obj['network_profile']['network_interfaces'][0]['id']
            pub_ip = self._get_az_pub_ip_from_nic_id(nic_id)

            ip = pub_ip.name

        req = self.network_client.public_ip_addresses.delete(self.GROUP_NAME,
                                                             ip)
        req.wait()
        Console.info(f"deleted pub ip {ip}")

    def _get_az_pub_ip_from_nic_id(self, nic_id):
        """
        TBD

        :param nic_id:
        :return:
        """
        pub_ip = None
        for ip in list(self.network_client.public_ip_addresses
                           .list(self.GROUP_NAME)):
            if ip.ip_configuration is not None and nic_id \
                in ip.ip_configuration.id:
                pub_ip = ip
        return pub_ip

    def _get_local_vm(self, vm_name, quiet=False):
        """
        TBD

        :param vm_name:
        :param quiet:
        :return:
        """
        vm_search = list(
            self.cmDatabase.collection('azure-vm').find({'name': vm_name}))

        if not quiet and len(vm_search) == 0:
            raise Exception(f"unable to locate {vm_name} in local db!")

        return vm_search[0] if len(vm_search) > 0 else None

    def _get_pub_ip_for_vm(self, vm):
        if isinstance(vm, dict):
            vm_obj = vm
        else:
            vm_obj = self._get_local_vm(vm)

        nic_id = vm_obj['network_profile']['network_interfaces'][0]['id']

        pub_ip = self._get_az_pub_ip_from_nic_id(nic_id)
        if pub_ip is None:
            raise Exception(f"unable to find public IP for {vm}")

        return vm_obj, pub_ip.as_dict()

    def ssh(self, vm=None, command=None):
        """
        TBD

        :param vm:
        :param command:
        :return:
        """

        if vm is None:
            raise Exception(f"vm or command can not be null")

        if command is None:
            command = ""

        vm_obj, pub_ip = self._get_pub_ip_for_vm(vm)

        # in the current API (vm/Provider), it does not provide a key name for
        # ssh. therefore, the key needs to be pulled from the vm. And therefore
        # key name is injected to the local db entry as 'ssh_key_name'
        key_obj = self._get_local_key_content(vm_obj['cm']['ssh_key_name'])

        cmd = "ssh " \
              "-o StrictHostKeyChecking=no " \
              "-o UserKnownHostsFile=/dev/null " \
              f"-i {key_obj['location']['private']} " \
              f"{self.USERNAME}@{pub_ip['ip_address']} {command}"
        cmd = cmd.strip()

        if command == "":
            if platform.lower() == 'win32':
                class disable_file_system_redirection:
                    _disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
                    _revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection

                    def __enter__(self):
                        self.old_value = ctypes.c_long()
                        self.success = self._disable(
                            ctypes.byref(self.old_value))

                    def __exit__(self, type, value, traceback):
                        if self.success:
                            self._revert(self.old_value)

                with disable_file_system_redirection():
                    os.system(cmd)
            else:
                os.system(cmd)
        else:
            if platform.lower() == 'win32':
                class disable_file_system_redirection:
                    _disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
                    _revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection

                    def __enter__(self):
                        self.old_value = ctypes.c_long()
                        self.success = self._disable(
                            ctypes.byref(self.old_value))

                    def __exit__(self, type, value, traceback):
                        if self.success:
                            self._revert(self.old_value)

                with disable_file_system_redirection():
                    Console.info('cmd: ' + cmd)
                    ssh = subprocess.Popen(cmd,
                                           shell=True,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
            else:
                Console.info('cmd: ' + cmd)
                ssh = subprocess.Popen(cmd,
                                       shell=True,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            result = ssh.stdout.read().decode("utf-8")
            if not result:
                error = ssh.stderr.readlines()
                Console.error(error)
            else:
                Console.info("cmd result: " + result)
                return result

    def _get_resource_group(self):
        groups = self.resource_client.resource_groups
        if groups.check_existence(self.GROUP_NAME):
            return groups.get(self.GROUP_NAME)
        else:
            # Create or Update Resource groupCreating new public IP
            Console.info('Creating Azure Resource Group')
            res = groups.create_or_update(self.GROUP_NAME,
                                          {'location': self.LOCATION})
            Console.info('Azure Resource Group created: ' + res.name)
            return res

    def set_server_metadata(self, name=None, cm=None):
        """
        TBD

        :param name:
        :param cm:
        :return:
        """
        # see https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-using-tags
        # https://github.com/Azure-Samples/virtual-machines-python-manage/blob/master/example.py
        # tags = FlatDict(cm)

        data = {}
        if cm is not None:
            data = {'cm': str(cm)}

        if name is None:
            name = self.VM_NAME

        async_vm_key_updates = self.vms.create_or_update(
            self.GROUP_NAME,
            name,
            {
                'location': self.LOCATION,
                'tags': data
            })
        async_vm_key_updates.wait()

        return async_vm_key_updates.result().tags

    def get_server_metadata(self, name):
        """
        TBD

        :param name:
        :return:
        """
        tags_dict = self.vms.get(self.GROUP_NAME, self.VM_NAME)

        return tags_dict.tags

    def delete_server_metadata(self, name, key):
        """
        TBD

        :param name:
        :param key:
        :return:
        """
        tags_dict = self.get_server_metadata(self)

        if key is not None:
            try:
                tags_dict.pop(key)
            except KeyError:
                print("Key " + key + " not found")

        async_vm_tag_updates = self.vms.update(self.GROUP_NAME, self.VM_NAME,
                                               {
                                                   'tags': tags_dict
                                               })
        async_vm_tag_updates.wait()

        return async_vm_tag_updates.result().tags

    def list_secgroups(self, name=None):
        """
        List the security group by name

        :param name: The name of the group, if None all will be returned
        :return:
        """
        local_sec_groups = self._get_local_sec_groups(name)
        Console.info('Local security groups: ')
        [Console.info(str(i)) for i in local_sec_groups]

        az_sec_groups = self._get_az_sec_groups(name)
        Console.info('Az security groups: ')
        [Console.info(str(i.__dict__)) for i in az_sec_groups]

        return local_sec_groups

    def _get_az_sec_groups(self, name=None):
        """
        TBD

        :param name:
        :return:
        """
        groups = self.network_client.network_security_groups.list(
            self.GROUP_NAME)
        ret = []
        for res in groups:
            if name is not None:
                if name == res.name:
                    ret.append(res)
            else:
                ret.append(res)

        return ret

    def _get_local_sec_groups(self, name=None):
        """
        TBD

        :param name:
        :return:
        """
        # if name is none, return all the groups, else filter the groups by name
        query = {} if name is None else {'name': name}

        local_sec_group = \
            self.cmDatabase.collection('local-secgroup').find(query)

        if local_sec_group.count() == 0:
            raise ValueError(f'No security groups were not found in '
                             f'local db for: {name}')

        res = list(local_sec_group)

        return _remove_mongo_id_obj(res)

    def _get_local_sec_rules(self, group_name=None):
        """
        TBD

        :param group_name:
        :return:
        """
        # if group_name is none, return all sec rules
        sec_rules = None
        if group_name is None:
            sec_rules = list(
                self.cmDatabase.collection('local-secrule').find({}))
        else:
            group = self._get_local_sec_groups(group_name)
            query = {'name': {'$in': group[0]['rules']}}
            sec_rules = list(
                self.cmDatabase.collection('local-secrule').find(query)
            )

        return _remove_mongo_id_obj(sec_rules)

    def list_secgroup_rules(self, name='default'):
        """
        List the security group rules by for provided Network Security Group

        :param name: The name of the group
        :return:
        """
        local_sec_rules = self._get_local_sec_rules(name)
        Console.info(f'local security rules for \'{name}\': '
                     f'{str(local_sec_rules)}')

        try:
            az_sec_rules = self.network_client.security_rules.list(
                self.GROUP_NAME, name)
            Console.info(f'az security rules for \'{name}\': ')
            [Console.info(i.__str__()) for i in az_sec_rules]
        except CloudError as e:
            Console.warning("Error in pulling sec rules: " + str(e))

    def _sec_rules_local_to_az(self, sec_rule_names):
        """
        TBD

        :param sec_rule_names:
        :return:
        """
        # local rules from the db
        sec_rules = self.cmDatabase.collection('local-secrule').find(
            {'name': {'$in': sec_rule_names}})

        az_sec_rules = []
        priority = 100
        for rule in sec_rules:
            az_rule = SecurityRule(
                protocol=self.protocol_str_map.get(rule['protocol'].lower()),
                name=rule['name'],
                access='Allow',  # todo: can only set Allows!
                direction='Inbound',  # todo: add appropriate
                source_address_prefix='*',  # todo: add appropriate
                destination_address_prefix='*',  # todo: add appropriate
                source_port_range='*',  # todo: add appropriate
                destination_port_range='*',  # todo: add appropriate
                priority=priority
            )
            az_sec_rules.append(az_rule)
            priority = priority + 1

        return az_sec_rules

    def _add_local_sec_group(self, name, description):
        """
        TBD

        :param name:
        :param description:
        :return:
        """
        add_group = {
            "description": description,
            "rules": [],
            "name": name,
            "cm": {
                "kind": "secgroup",
                "name": name,
                "cloud": "local",
                "collection": "local-secgroup",
                "created": str(datetime.now()),
                "modified": str(datetime.now())
            }
        }

        self.cmDatabase.collection('local-secgroup').insert_one(add_group)
        return add_group

    def _add_az_sec_group(self, name):
        """
        TBD

        :param name:
        :return:
        """
        parameters = {
            'location': self.LOCATION,
        }

        result_add_security_group = self.network_client. \
            network_security_groups.create_or_update(self.GROUP_NAME, name,
                                                     parameters)

        return result_add_security_group.result()

    def add_secgroup(self, name=None, description=None):
        """
        Adds the sec group locally
        :param name: Name of the group
        :param description: The description
        :return:
        """
        if name is None:
            name = 'default'

        try:
            local_sec_group = self._get_local_sec_groups(name)[0]
            Console.info(f"local sec group: {str(local_sec_group)}")
        except ValueError:
            local_sec_group = self._add_local_sec_group(name, description)
            Console.warning(f'{name} sec group is not found! Created new '
                            f'group: {str(local_sec_group)}')

        # self._add_az_sec_group(name)

        Console.info("sec group created successfully!")
        return local_sec_group

    def add_secgroup_rule(self,
                          name=None,  # group name
                          port=None,
                          protocol=None,
                          ip_range=None):
        """
        Adding sec rule to the local db as azure does not support explicit sec
        rules
        :param name:
        :param port:
        :param protocol:
        :param ip_range:
        :return:
        """
        # todo: change these defaults
        protocol = "tcp" if protocol is None else protocol
        ip_range = "0.0.0.0/0" if ip_range is None else ip_range
        port = "22:22" if port is None else port
        name = "ssh" if name is None else name

        add_rule = self.update_dict({
            "protocol": protocol,
            "ip_range": ip_range,
            "ports": port,
            "name": name,
        }, kind='secrule')[0]

        self.cmDatabase.collection('local-secrule').insert_one(add_rule)

        return add_rule

    def remove_secgroup(self, name=None):
        """
        Delete the names security group

        :param name: The name of the Security Group to be deleted
        :return:
        """

        del_group = self.network_client.network_security_groups. \
            delete(self.GROUP_NAME, name)
        del_group.wait()
        Console.info(f'Security group {name} deleted from Az!')

    def upload_secgroup(self, name=None):
        """
        Takes the security group from the local db and push it to az
        :param name:
        :return:
        """
        local_group = self._get_local_sec_groups(name)[0]

        # transform local rules to az rule objects
        az_rules = self._sec_rules_local_to_az(local_group['rules'])

        # add az sec group
        self._add_az_sec_group(name)

        # push az rules
        results = []
        for az_rule in az_rules:
            ret = self.network_client.security_rules.create_or_update(
                self.GROUP_NAME,
                local_group['name'],
                az_rule.name,
                az_rule
            )

            results.append(ret.result().as_dict())

        return results

    def _check_local_rules_available(self, rules):
        """
        TBD

        :param rules:
        :return:
        """
        sec_rules = self.cmDatabase.collection('local-secrule').find(
            {'name': {'$in': rules}})
        rule_names = {i['name'] for i in sec_rules}

        if len(rule_names) == rules:
            raise ValueError(f'Some of the security rules are not available: '
                             f'{str(rules)}')

    def add_rules_to_secgroup(self, secgroupname=None, newrules=None):
        """
        Adds the rules to te local sec group only! it will update the az sec
        group once it is uploaded
        :param secgroupname:
        :param newrules:
        :return:
        """
        if secgroupname is None and newrules is None:
            raise ValueError("name or rules are None")

        if not isinstance(newrules, list):
            raise ValueError('rules should be a list')

        sec_group = self._get_local_sec_groups(secgroupname)[0]
        current_rules = set(sec_group['rules'])

        # check if the rules are already available
        self._check_local_rules_available(newrules)

        current_rules.update(newrules)

        cm = sec_group['cm']
        cm.update({"modified": str(datetime.now())})

        update = {"$set": {"rules": list(current_rules), "cm": cm, }}
        query = {'name': secgroupname}

        self.cmDatabase.collection('local-secgroup').update_one(query, update)

        return self._get_local_sec_groups(secgroupname)[0]

    def remove_rules_from_secgroup(self, name=None, rules=None):
        """
        removes rules from a secgroup both locally and from azure group
        :param name:
        :param rules:
        :return:
        """

        local_group = self._get_local_sec_groups(name)[0]
        new_rules = local_group['rules']
        [new_rules.remove(i) for i in rules]

        cm = local_group['cm']
        cm.update({"modified": str(datetime.now())})

        update = {"$set": {"rules": new_rules, "cm": cm, }}
        query = {'name': name}

        self.cmDatabase.collection('local-secgroup').update_one(query, update)
        Console.info(f'Security rules {str(rules)} locally!')

        if isinstance(rules, list):
            [self.network_client.security_rules.delete(self.GROUP_NAME, name,
                                                       r).wait() for r in rules]
        else:
            self.network_client.security_rules.delete(self.GROUP_NAME,
                                                      name,
                                                      rules).wait()
        Console.info(f'Security rules {str(rules)} from az!')

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
               flavor=None,
               **kwargs):
        """
        creates a named node

        :param name: the name of the node
        :param image: the image used
        :param size: the size of the image
        :param timeout: a timeout in seconds that is invoked in case the image
                        does not boot. The default is set to 3 minutes.
        :param kwargs: additional arguments passed along at time of boot
        :param location:
        :param key:
        :param secgroup:
        :param ip:
        :param user:
        :param public:
        :param group:
        :param metadata:
        :param flavor:
        :return:

        """
        if group is None:
            group = self.GROUP_NAME

        if name is None:
            name = self.VM_NAME

        if secgroup is None:
            secgroup = 'default'

        if ip is None:
            pub_ip = self.find_available_public_ip()[0]
        else:
            pub_ip = self._get_az_public_ip(ip)

        if key is None:
            key = self.user

        if flavor is None:
            flavor = 'Standard_B1s'

        vm_parameters = self._create_vm_parameters(name, secgroup, pub_ip, key,
                                                   flavor)
        banner("Creating Server")
        Console.msg(f"    Name:     {name}")
        Console.msg(f"    User:     {user}")
        Console.msg(f"    IP:       {pub_ip['name']}")
        Console.msg(f"    Image:    {image}")
        Console.msg(f"    Size:     {size}")
        Console.msg(f"    Public:   ?")
        Console.msg(f"    Key:      {key}")
        Console.msg(f"    Location: {location}")
        Console.msg(f"    Timeout:  {timeout}")
        Console.msg(f"    Secgroup: {secgroup}")
        Console.msg(f"    Group:    {group}")
        Console.msg("")

        vm = self.vms.create_or_update(
            group,
            name,
            vm_parameters).result()

        Console.info('VM created: ' + vm.name)

        #  todo data disk creation is taken off due to cost limitations!
        # disks_count = len(
        #     list(self.compute_client.disks.list_by_resource_group(group)))
        #
        # # Creating a Managed Data Disk
        # async_disk_creation = self.compute_client.disks.create_or_update(
        #     group,
        #     f"{self.OS_DISK_NAME}_{disks_count}",
        #     {
        #         'location': self.LOCATION,
        #         'disk_size_gb': 8,
        #         'creation_data': {
        #             'create_option': 'Empty'
        #         }
        #     }
        # )
        # data_disk = async_disk_creation.result()
        #
        # # Get the virtual machine by name
        # virtual_machine = self.vms.get(
        #     group,
        #     name
        # )
        #
        # # Attaching Data Disk to a Virtual Machine
        # virtual_machine.storage_profile.data_disks.append({
        #     'lun': 0,
        #     'name': data_disk.name,
        #     'create_option': 'Attach',
        #     'managed_disk': {
        #         'id': data_disk.id
        #     }
        # })
        # updated_vm = self.vms.create_or_update(
        #     group,
        #     name,
        #     virtual_machine
        # )
        # updated_dict = updated_vm.result().as_dict()

        updated_dict = vm.as_dict()
        updated_dict['status'] = 'ACTIVE'
        updated_dict['ssh_key_name'] = key

        _, pub_ip = self._get_pub_ip_for_vm(updated_dict)
        updated_dict['public_ip'] = pub_ip['ip_address']

        return self.update_dict(updated_dict, kind='vm')[0]

    def _get_local_key_content(self, key_name):
        """
        TBD

        :param key_name:
        :return:
        """
        query = {'name': key_name}

        key = list(self.cmDatabase.collection('local-key').find(query))

        if len(key) == 0:
            raise ValueError(f'Unable to find key: {key_name}')

        return key[0]

    def _create_vm_parameters(self, name, secgroup, ip, key, flavor):
        """
        Create the VM parameters structure.
        :param secgroup: sec group name
        :param ip: az PublicIP object as dict
        :param key: pub key content
        :return:
        """

        nic = self._create_az_nic(secgroup, ip)

        # # Parse Image from yaml file
        publisher, offer, sku, version = self.default["image"].split(":")

        # Declare Virtual Machine Settings
        vm_parameters = {
            'location': self.LOCATION,
            'os_profile': {
                'computer_name': name,
                'admin_username': self.USERNAME,
                'admin_password': self.PASSWORD,
                'linux_configuration': {
                    'ssh': {
                        'public_keys': [{
                            'path': "/home/" + self.USERNAME +
                                    "/.ssh/authorized_keys",
                            'key_data':
                                str(self._get_local_key_content(key)
                                    ['public_key']),
                        }]
                    }
                }
            },
            'hardware_profile': {
                'vm_size': flavor,
            },
            'storage_profile': {
                'image_reference': {
                    'publisher': publisher,
                    'offer': offer,
                    'sku': sku,
                    'version': version
                },
                'os_disk': {
                    'name': f"{self.OS_DISK_NAME}_{name}",
                    'create_option': 'FromImage',
                    'disk_size_gb': 64,
                    'managed_disk': {
                        'storage_account_type': 'Premium_LRS',
                    }
                }
            },
            'network_profile': {
                'network_interfaces': [{
                    'id': nic.id,
                }]
            },
        }

        return vm_parameters

    def _create_az_sec_group_if_not_exists(self, sec_group_name):
        """
        TBD

        :param sec_group_name:
        :return:
        """
        az_group = self._get_az_sec_groups(sec_group_name)

        if len(az_group) > 0:
            Console.info(f"secgroup {sec_group_name} exists!")
        else:
            self.upload_secgroup(sec_group_name)

    def _create_az_vnet_if_not_exists(self):
        """
        TBD

        :return:
        """
        for vnet in self.network_client.virtual_networks.list(self.GROUP_NAME):
            if vnet.name == self.VNET_NAME:
                Console.info(f"vnet {vnet.name} exists!")
                return vnet

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
        res = async_vnet_creation.result()
        Console.info("VNET created: " + res.name)
        return res

    def _create_az_subnet_if_not_exitsts(self, secgroup):
        """
        TBD

        :param secgroup:
        :return:
        """
        for subnet in self.network_client.subnets.list(self.GROUP_NAME,
                                                       self.VNET_NAME):
            if subnet.name == self.SUBNET_NAME:
                Console.info(f"subnet {subnet.name} exists!")
                return subnet

        subnet_params = {
            'address_prefix': '10.0.0.0/24',
            'network_security_group': {
                'id': self._get_az_sec_groups(name=secgroup)[0].id
            }
        }

        async_subnet_creation = self.network_client.subnets.create_or_update(
            self.GROUP_NAME,
            self.VNET_NAME,
            self.SUBNET_NAME,
            subnet_parameters=subnet_params,
        )

        res = async_subnet_creation.result()
        Console.info("Subnet created: " + res.name)
        return res

    def _create_az_nic(self, secgroup, ip):
        """
        Create a Network Interface for a Virtual Machine

        :param secgroup:
        :param ip:
        :return:
        """
        # A Resource group needs to be in place
        self._get_resource_group()

        # create sec group
        self._create_az_sec_group_if_not_exists(secgroup)

        # Create Virtual Network
        Console.info('Creating Vnet')
        vnet = self._create_az_vnet_if_not_exists()

        # Create Subnet
        Console.info('Creating Subnet')
        subnet = self._create_az_subnet_if_not_exitsts(secgroup)

        # Create NIC
        Console.info('Creating NIC')

        # each vm needs a nic. so, use self.NIC_NAME as a prefix for the NICs
        nic_count = len(
            list(self.network_client.network_interfaces.list(self.GROUP_NAME)))

        nic_params = {
            'location': self.LOCATION,
            'ip_configurations': [{
                'name': self.IP_CONFIG_NAME,
                'subnet': {
                    'id': subnet.id
                },
                'public_ip_address': {
                    'id': ip['id']
                }
            }],
            'network_security_group': {
                'id': subnet.network_security_group.id,
            }
        }

        nic = self.network_client.network_interfaces.create_or_update(
            self.GROUP_NAME,
            f"{self.NIC_NAME}_{nic_count}",
            parameters=nic_params,
        ).result()

        Console.info("NIC created: " + nic.name)

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
        Console.info('Starting Azure VM')
        async_vm_start = self.vms.start(group, name)
        async_vm_start.wait()
        return self.info(group, name, 'ACTIVE')

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
        Console.info('Restarting Azure VM')
        async_vm_restart = self.vms.restart(group, name)
        async_vm_restart.wait()

        return self.info(group, name, 'REBOOT')

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
        Console.info('Stopping Azure VM')
        async_vm_stop = self.vms.power_off(group, name)
        async_vm_stop.result()
        return self.info(group, name, 'SHUTOFF')

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
        # TODO: Joaquin -> Completed
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

        return self.power_off(group, name)

    def info(self, group=None, name=None, status=None):
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

        node = self.vms.get(group, name, expand='instanceView')

        nodedict = node.as_dict()

        az_status = node.instance_view.statuses[-1].code.lower()
        nodedict['status'] = _get_az_vm_status(az_status)

        return self.update_dict(nodedict, kind='vm')

    def status(self, name=None):
        """
        TBD

        :param name:
        :return:
        """
        r = self.cloudman.list_servers(filters={'name': name})[0]
        return r['status']

    def list(self):
        """
        List all Azure Virtual Machines from my Account

        :return: dict
        """
        az_servers = []

        for vm in self.vms.list(self.GROUP_NAME):
            v = vm.as_dict()
            local_vm = self._get_local_vm(v['name'], quiet=True)

            if local_vm is None:
                Console.warning("no local vm found for " + v['name'])

            v.update(local_vm)
            az_servers.append(v)

        return self.update_dict(az_servers, kind="vm")

    def destroy(self, name=None):
        """
        Destroys the node

        :param name: the name of the node
        :return: the dict of the node
        """
        if name is None:
            vms = self.list()
        else:
            vms = filter(lambda x: x['name'] == name, self.list())

        # Delete vms
        res = []
        for vm in vms:
            elm = {}
            Console.info('Deleting Azure Virtual Machine')
            del_vm = self.vms.delete(self.GROUP_NAME, vm['name'])
            del_vm.wait()

            elm['name'] = vm['name']
            elm['status'] = 'TERMINATED'
            elm['type'] = vm['type']
            elm['location'] = vm['location']
            res.append(elm)

        res = self.update_dict(res, kind='vm')

        # # Delete Resource Group
        Console.info('Deleting Azure Resource Group')
        async_group_delete = \
            self.resource_client.resource_groups.delete(self.GROUP_NAME)
        async_group_delete.wait()

        return res

    def images(self, **kwargs):
        """
        Lists the images on the cloud

        :param kwargs:
        :return: dict
        """
        region = self.LOCATION

        image_list = list()

        result_list_pub = self.imgs.list_publishers(
            region,
        )
        i = 0

        for publisher in result_list_pub:
            if (i < 5):
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
                                            Console.debug_msg(str(msg))
                                            image_list.append(result_get)
                                        except:
                                            print(
                                                "Something failed in result_list")

                                except:
                                    print(
                                        "Something failed in result_list_skus")

                        except:
                            print("Something failed in result_list_offers")

                except:
                    print("Something failed in result_list_pub")
            i = i + 1
        return self.get_list(image_list, kind="image")

    def flavors(self):
        """
        Lists the flavors on the cloud

        :return: dict of flavors
        """
        vm_sizes_list = self.compute_client.virtual_machine_sizes.list(
            location=self.LOCATION)

        return self.get_list(vm_sizes_list, kind="flavor")

    def flavor(self, name=None):
        """
        Gets the flavor with a given name

        :param name: The name of the flavor
        :return: The dict of the flavor
        """
        return self.find(self.flavors(), name=name)

    def find(self, elements, name=None):
        """
        Finds an element in elements with the specified name.

        :param elements: The elements
        :param name: The name to be found
        :return:
        """

        for element in elements:
            if element["name"] == name or element["cm"]["name"] == name:
                return element
        return None

    def image(self, name=None, **kwargs):
        """
        Gets the image with a given nmae

        :param name: The name of the image
        :param kwargs:
        :return: the dict of the image
        """
        return self.find(self.images(**kwargs), name=name)

    def get_list(self, d, kind=None, debug=False, **kwargs):
        """
        Lists the dict d on the cloud

        :param d:
        :param kind:
        :param debug:
        :param kwargs:
        :return: dict
        """
        if self.vms:
            entries = []
            for entry in d:
                entries.append(entry.as_dict())
            if debug:
                pprint(entries)

            return self.update_dict(entries, kind=kind)
        return None

    def rename(self, name=None, destination=None):
        # TODO: Azure Provider rename function not implemented
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
        The cloud returns an object or list of objects With the dict method this
        object is converted to a cloudmesh dict. Typically this method is used
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

        for entry in _elements:

            if "cm" not in entry.keys():
                entry['cm'] = {}

            entry["cm"].update({
                "kind": kind,
                "driver": self.cloudtype,
                "cloud": self.cloud,
                "name": entry['name']
            })

            if kind == 'vm':
                entry["cm"]["updated"] = str(datetime.utcnow())
                entry["cm"]["name"] = entry["name"]
                entry["cm"]["type"] = entry[
                    "type"]  # Check feasibility of the following items
                entry["cm"]["location"] = entry[
                    "location"]  # Check feasibility of the following items
                if 'status' in entry.keys():
                    entry["cm"]["status"] = str(entry["status"])
                if 'ssh_key_name' in entry.keys():
                    entry["cm"]["ssh_key_name"] = str(entry["ssh_key_name"])

            elif kind == 'flavor':

                entry["cm"]["created"] = str(datetime.utcnow())
                entry["cm"]["name"] = entry["name"]
                entry["cm"]["number_of_cores"] = entry["number_of_cores"]
                entry["cm"]["os_disk_size_in_mb"] = entry["os_disk_size_in_mb"]
                entry["cm"]["resource_disk_size_in_mb"] = entry[
                    "resource_disk_size_in_mb"]
                entry["cm"]["memory_in_mb"] = entry["memory_in_mb"]
                entry["cm"]["max_data_disk_count"] = entry[
                    "max_data_disk_count"]
                entry["cm"]["updated"] = str(datetime.utcnow())

            elif kind == 'image':

                entry['cm']['created'] = str(datetime.utcnow())
                entry['cm']['updated'] = str(datetime.utcnow())
                entry["cm"]["name"] = entry["name"]

            elif kind == 'secgroup':

                entry["cm"]["name"] = entry["name"]
                entry['cm']['created'] = str(datetime.utcnow())
                entry['cm']['updated'] = str(datetime.utcnow())

            elif kind == 'key':

                entry['cm']['created'] = str(datetime.utcnow())
                entry['cm']['updated'] = str(datetime.utcnow())

            elif kind == 'secrule':

                entry['cm']['created'] = str(datetime.utcnow())
                entry['cm']['updated'] = str(datetime.utcnow())

            d.append(entry)
            # VERBOSE(d, verbose=10)

        return d

    def wait(self,
             vm=None,
             interval=None,
             timeout=None):
        """
        TBD

        :param vm:
        :param interval:
        :param timeout:
        :return:
        """
        return self.list()
