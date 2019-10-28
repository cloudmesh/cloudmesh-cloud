from ast import literal_eval
from datetime import datetime
from pprint import pprint

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network.v2018_12_01.models import NetworkSecurityGroup, \
    SecurityRule
from cloudmesh.common3.DictList import DictList
from cloudmesh.common.Printer import Printer
import azure.mgmt.network.models
from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.provider import ComputeProviderPlugin
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.configuration.Config import Config
from msrestazure.azure_exceptions import CloudError

CLOUDMESH_YAML_PATH = "~/.cloudmesh/cloudmesh.yaml"


def _remove_mongo_id_obj(dict_list):
    for i in dict_list:
        try:
            i.pop('_id')
        except KeyError:
            pass

    return dict_list


class Provider(ComputeNodeABC, ComputeProviderPlugin):
    kind = 'azure'

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
        self.NIC_NAME = self.default["AZURE_VM_NIC"]

        # public IPs
        self.PUBLIC_IP__NAME = self.default['AZURE_PUBLIC_IP_NAME']

        # Azure VM Storage details
        self.OS_DISK_NAME = self.default["AZURE_VM_DISK_NAME"]
        self.USERNAME = self.default["AZURE_VM_USER"]
        self.PASSWORD = self.default["AZURE_VM_PASSWORD"]
        self.VM_NAME = self.default["AZURE_VM_NAME"]

        # Create or Update Resource group
        self.get_resource_group()

        self.cmDatabase = CmDatabase()

        self.protocol_str_map = {
            'tcp': 'Tcp',
            'udp': 'Udp',
            '*': '*'
        }

    def Print(self, data, output=None, kind=None):
        # TODO: Joaquin

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
        # TODO: Moeen
        raise NotImplementedError

    def key_upload(self, key=None):
        # TODO: Moeen
        raise NotImplementedError

    def key_delete(self, name=None):
        # TODO: Moeen
        raise NotImplementedError

    def get_public_ip(self, name=None):
        raise NotImplementedError

    # these are available to be associated
    def list_public_ips(self, ip=None, available=False):
        """
        lists public ips of the group
        """
        list_result = self.network_client.public_ip_addresses.list(
            self.GROUP_NAME)

        return list_result

    def delete_public_ip(self, ip=None):
        """
        deletes public ip by name
        """
        if ip is not None:
            res = self.network_client.public_ip_addresses.delete(
                self.GROUP_NAME,
                ip
            )

            return res.result()
        else:
            Console.warning('No ip prefix provided')
            return None

    def create_public_ip(self):
        """
        Creates public IP for the group with the ip name provided in the config
        :return:
        """

        public_ip_params = {
            'location': self.LOCATION,
            'public_ip_allocation_method': 'Static',
            'sku': {
                'name': 'Basic',
            }
        }

        creation_result = self.network_client.public_ip_addresses.create_or_update(
            self.GROUP_NAME,
            self.PUBLIC_IP__NAME,
            public_ip_params,
            # custom_headers={'Accept': 'application/json'}
        )

        return creation_result.result()

    def find_available_public_ip(self):
        """
        ip will be quarried using the name provided in the config

        if no ip is available, create the IP and return the publicIP object.
        else, if IP is available and free, return that object
        else throw and error

        :return:
        """
        ip = next((x for x in self.list_public_ips() if
                   x.name == self.PUBLIC_IP__NAME), None)

        if ip is None:
            # if ip is none -> no ip available --> create it!
            return self.create_public_ip()
        elif ip.ip_configuration is None:
            # if ip_configuration is none -> ip is available --> return it!
            return ip
        else:
            raise Exception('IP is already allocated!: ' + self.PUBLIC_IP__NAME)

    def attach_public_ip(self, node=None, ip=None):
        """
        attaches a public ip to a node
        """
        ip = self.find_available_public_ip()

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
                'ip_configurations': [ip_config]
            }
        )

        return res.result()

    def detach_public_ip(self, node=None, ip=None):
        # TODO: Moeen
        raise NotImplementedError

    # see the openstack example it will be almost the same as in openstack
    # other than getting
    # the ip and username
    def ssh(self, vm=None, command=None):
        raise NotImplementedError

    def get_resource_group(self):
        # TODO: Joaquin -> Completed

        groups = self.resource_client.resource_groups
        if groups.check_existence(self.GROUP_NAME):
            return groups.get(self.GROUP_NAME)
        else:
            # Create or Update Resource group
            VERBOSE(" ".join('Create Azure Resource Group'))
            return groups.create_or_update(
                self.GROUP_NAME, {'location': self.LOCATION})

    def set_server_metadata(self, name=None, cm=None):
        # see https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-using-tags
        # https://github.com/Azure-Samples/virtual-machines-python-manage/blob/master/example.py
        # TODO: Joaquin -> Completed
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
        # TODO: Joaquin -> Completed
        tags_dict = self.vms.get(self.GROUP_NAME, self.VM_NAME)

        return tags_dict.tags

    def delete_server_metadata(self, name, key):
        # TODO: Joaquin -> Completed

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
        # TODO: Joaquin -> Completed
        """
        List the security group by name

        :param name: The name of the group, if None all will be returned
        :return:
        """

        # groups = self.network_client.network_security_groups.list_all(self)
        #
        # if name is not None:
        #     for entry in groups:
        #         if entry['name'] == name:
        #             groups = [entry]
        #             break
        #
        # return self.get_list(
        #     groups,
        #     kind="secgroup")

        local_sec_groups = self._get_local_sec_groups(name)
        Console.info('Local security groups: ')
        [Console.info(str(i)) for i in local_sec_groups]

        az_sec_groups = self._get_az_sec_groups(name)
        Console.info('Az security groups: ')
        [Console.info(i.__str__()) for i in az_sec_groups]

        return local_sec_groups

    def _get_az_sec_groups(self, name=None):
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
        # TODO: Joaquin
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
        # local rules from the db
        sec_rules = self.cmDatabase.collection('local-secrule').find(
            {'name': {'$in': sec_rule_names}})

        az_sec_rules = []
        priority = 100
        for rule in sec_rules:
            az_rule = SecurityRule(
                protocol=self.protocol_str_map.get(rule['protocol']),
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
        parameters = {
            'location': self.LOCATION,
        }

        result_add_security_group = self.network_client. \
            network_security_groups.create_or_update(self.GROUP_NAME, name,
                                                     parameters)
        result_add_security_group.wait()

        return result_add_security_group.result()

    def add_secgroup(self, name='default', description=None):
        # TODO: Joaquin -> Completed
        """
        Adds the
        :param name: Name of the group
        :param description: The description
        :return:
        """
        try:
            local_sec_group = self._get_local_sec_groups(name)[0]
            Console.info(f"local sec group: {str(local_sec_group)}")
        except ValueError:
            local_sec_group = self._add_local_sec_group(name, description)
            Console.warning(f'{name} sec group is not found! Created new '
                            f'group: {str(local_sec_group)}')

        self._add_az_sec_group(name)

        Console.info("sec group created successfully!")
        return local_sec_group

    def add_secgroup_rule(self,
                          name=None,  # group name
                          port=None,
                          protocol=None,
                          ip_range=None):
        # TODO: Joaquin -> Completed

        # network_sec_group_name = 'cloudmesh_jae'

        # if self.network_client:
        #     # list all the rules available
        #     sec_rules = self.list_secgroup_rules(name)
        #
        #     try:
        #         portmin, portmax = port.split(":")
        #     except:
        #         portmin = None
        #         portmax = None
        #
        #     parameters = SecurityRule(
        #         access=azure.mgmt.network.models.SecurityRuleAccess.allow,
        #         priority=500,
        #         destination_address_prefix='*',
        #         destination_port_range='*',
        #         direction=azure.mgmt.network.models.SecurityRuleDirection.inbound,
        #         protocol=azure.mgmt.network.models.SecurityRuleProtocol.tcp,
        #         source_address_prefix='*',
        #         source_port_range='*'
        #     )
        #
        # else:
        #     raise ValueError("cloud not initialized")
        #
        # add_rule = self.network_client.security_rules.create_or_update(
        #     self.GROUP_NAME, network_sec_group_name, name, parameters)

        # this method would add sec group rule to local db only, because azure
        # does not support adding security rules without security group names
        # todo: change these defaults
        protocol = "tcp" if protocol is None else protocol
        ip_range = "0.0.0.0/0" if ip_range is None else ip_range
        port = "22:22" if port is None else port
        name = "ssh" if name is None else name

        add_rule = {
            "protocol": protocol,
            "ip_range": ip_range,
            "ports": port,
            "name": name,
            "cm": {
                "kind": "secrule",
                "name": name,
                "cloud": "local",
                "collection": "local-secrule",
                "created": str(datetime.now()),
                "modified": str(datetime.now()),
            }
        }
        self.cmDatabase.collection('local-secrule').insert_one(add_rule)

        return add_rule

    def remove_secgroup(self, name=None):
        # TODO: Joaquin -> Completed
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
        # TODO: Joaquin -> Completed
        # cgroups = self.list_secgroups(name)
        # group_exists = False
        # if len(cgroups) > 0:
        #     print("Warning group already exists")
        #     group_exists = True
        #
        # groups = NetworkSecurityGroup().list()
        # rules = SecurityRule().list()
        #
        # # pprint (rules)
        # data = {}
        # for rule in rules:
        #     data[rule['name']] = rule
        #
        # # pprint (groups)
        #
        # for group in groups:
        #     if group['name'] == name:
        #         break
        # print("upload group:", name)
        #
        # if not group_exists:
        #     self.add_secgroup(name=name, description=group['description'])
        #
        #     for r in group['rules']:
        #         found = data[r]
        #         print("    ", "rule:", found['name'])
        #         self.add_secgroup_rule(
        #             name=name,
        #             port=found["ports"],
        #             protocol=found["protocol"],
        #             ip_range=found["ip_range"])
        #
        # else:
        #
        #     for r in group['rules']:
        #         found = data[r]
        #         print("    ", "rule:", found['name'])
        #         self.add_rules_to_secgroup(
        #             name=name,
        #             rules=[found['name']])

        # this method would get the security group from the local db and push it
        # to az
        local_group = self._get_local_sec_groups(name)[0]

        # transform local rules to az rule objects
        az_rules = self._sec_rules_local_to_az(local_group['rules'])

        # push az rules
        results = []
        for az_rule in az_rules:
            ret = self.network_client.security_rules.create_or_update(
                self.GROUP_NAME,
                local_group['name'],
                az_rule.name,
                az_rule
            )

            results.append(ret.result())

        return results

    def _check_local_rules_available(self, rules):
        sec_rules = self.cmDatabase.collection('local-secrule').find(
            {'name': {'$in': rules}})
        rule_names = {i['name'] for i in sec_rules}

        if len(rule_names) == rules:
            raise ValueError(f'Some of the security rules are not available: '
                             f'{str(rules)}')

    def add_rules_to_secgroup(self, name=None, rules=None):
        # TODO: Joaquin -> Completed

        if name is None and rules is None:
            raise ValueError("name or rules are None")

        if not isinstance(rules, list):
            raise ValueError('rules should be a list')

        # cgroups = self.list_secgroups(name)
        # if len(cgroups) == 0:
        #     raise ValueError("group does not exist")
        #
        # groups = DictList(NetworkSecurityGroup().list())
        # rules_details = DictList(SecurityRule().list())
        #
        # try:
        #     group = groups[name]
        # except:
        #     raise ValueError("group does not exist")
        #
        # for rule in rules:
        #     try:
        #         found = rules_details[rule]
        #         self.add_secgroup_rule(name=name,
        #                                port=found["ports"],
        #                                protocol=found["protocol"],
        #                                ip_range=found["ip_range"])
        #     except:
        #         ValueError("rule can not be found")

        # this method will add the rules to te local sec group only! it will
        # update the az sec group once it is uploaded
        sec_group = self._get_local_sec_groups(name)[0]
        current_rules = sec_group['rules']

        # check if the rules are already available
        self._check_local_rules_available(rules)

        current_rules.extend(rules)

        cm = sec_group['cm']
        cm.update({"modified": str(datetime.now())})

        update = {
            "$set": {
                "rules": current_rules,
                "cm": cm,
            }
        }

        query = {'name': name}

        self.cmDatabase.collection('local-secgroup').update_one(query, update)

        return self._get_local_sec_groups(name)[0]

    def remove_rules_from_secgroup(self, name=None, rules=None):
        # TODO: Joaquin -> Completed

        local_group = self._get_local_sec_groups(name)[0]
        new_rules = local_group['rules']
        [new_rules.remove(i) for i in rules]

        cm = local_group['cm']
        cm.update({"modified": str(datetime.now())})

        update = {
            "$set": {
                "rules": new_rules,
                "cm": cm,
            }
        }
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
               **kwargs):
        # TODO: Joaquin -> Completed
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

        if group is None:
            group = self.GROUP_NAME
        if name is None:
            name = self.VM_NAME

        async_vm_creation = self.vms.create_or_update(
            group,
            name,
            vm_parameters)
        async_vm_creation.wait()

        # Creating a Managed Data Disk
        async_disk_creation = self.compute_client.disks.create_or_update(
            group,
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
            group,
            name
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
            group,
            name,
            virtual_machine
        )
        async_disk_attach.wait()

        return self.info(group, name, 'ACTIVE')

    def create_vm_parameters(self):
        # TODO: Joaquin -> Completed
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
        # TODO: Joaquin -> Completed
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
        # TODO: Joaquin -> Completed
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
        return self.info(group, name, 'ACTIVE')

    def reboot(self, group=None, name=None):
        # TODO: Joaquin -> Completed
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

        return self.info(group, name, 'REBOOT')

    def stop(self, group=None, name=None):
        # TODO: Joaquin -> Completed
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
        return self.info(group, name, 'SHUTOFF')

    def resume(self, group=None, name=None):
        # TODO: Joaquin -> Completed
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
        # TODO: Joaquin -> Completed
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

        nodedict = node.as_dict()
        nodedict['status'] = status

        return self.update_dict(nodedict, kind='vm')

    def status(self, name=None):
        # TODO: Joaquin -> Completed
        r = self.cloudman.list_servers(filters={'name': name})[0]
        return r['status']

    def list(self):
        # TODO: Joaquin -> Completed
        """
        List all Azure Virtual Machines from my Account
        :return: dict or libcloud object
        """
        servers = self.vms.list_all()

        return self.get_list(servers, kind="vm")

    def destroy(self, group=None, name=None):
        # TODO: Joaquin -> Completed
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
        server = self.vms.delete(group, name)
        server.wait()

        # Delete Resource Group
        VERBOSE(" ".join('Deleting Azure Resource Group'))
        async_group_delete = self.resource_client.resource_groups.delete(
            group)
        async_group_delete.wait()

        server['status'] = 'DELETED'

        servers = self.update_dict([server], kind='vm')

        return servers

    def images(self, **kwargs):
        # TODO: Joaquin -> Completed
        """
        Lists the images on the cloud
        :return: dict or libcloud object
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
                                            VERBOSE(msg)
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
        # TODO: Joaquin -> Completed
        """
        Lists the flavors on the cloud

        :return: dict of flavors
        """
        vm_sizes_list = self.compute_client.virtual_machine_sizes.list(
            location=self.LOCATION)

        return self.get_list(vm_sizes_list, kind="flavor")

    def flavor(self, name=None):
        # TODO: Joaquin -> Completed
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

    def image(self, name=None):
        # TODO: Joaquin -> Completed
        """
        Gets the image with a given nmae
        :param name: The name of the image
        :return: the dict of the image
        """
        return self.find(self.images(**kwargs), name=name)

    def get_list(self, d, kind=None, debug=False, **kwargs):
        # TODO: Joaquin -> Completed
        """
        Lists the dict d on the cloud
        :return: dict or libcloud object
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
        # TODO: Joaquin -> Completed
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

        for entry in _elements:

            if "cm" not in entry:
                entry['cm'] = {}

            if kind == 'ip':
                entry['name'] = entry['floating_ip_address']

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
                if 'status' in entry:
                    entry["cm"]["status"] = str(entry["status"])

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
                if self.cloudtype == 'azure':
                    entry["cm"]["name"] = entry["name"]
                else:
                    pass

            d.append(entry)
            VERBOSE(d)

        return d

    def wait(self,
             vm=None,
             interval=None,
             timeout=None):
        raise NotImplementedError;
