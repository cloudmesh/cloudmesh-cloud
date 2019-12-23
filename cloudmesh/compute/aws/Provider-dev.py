from datetime import datetime

import os
import subprocess
import time
from sys import platform
import ctypes
from time import sleep

import boto3
from cloudmesh.common.Printer import Printer
from botocore.exceptions import ClientError
from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import banner
from cloudmesh.common.DictList import DictList
from cloudmesh.compute.aws.AwsFlavors import AwsFlavor
from cloudmesh.configuration.Config import Config
from cloudmesh.provider import ComputeProviderPlugin
from cloudmesh.mongo.DataBaseDecorator import DatabaseImportAsJson
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.common3.Shell import Shell
from cloudmesh.secgroup.Secgroup import Secgroup, SecgroupRule
from cloudmesh.common.util import path_expand
from cloudmesh.common.Benchmark import Benchmark
import json
from cloudmesh.management.configuration.name import Name


class Provider(ComputeNodeABC, ComputeProviderPlugin):
    kind = "aws"

    sample = """
    cloudmesh:
      cloud:
        {name}:
          cm:
            active: true
            heading: AWS
            host: TBD
            label: {name}
            kind: aws
            version: TBD
            service: compute
          default:
            image: ami-0c929bde1796e1484
            size: t2.medium
          credentials:
            region: {region}
            EC2_SECURITY_GROUP: cloudmesh
            EC2_ACCESS_ID: {EC2_ACCESS_ID}
            EC2_SECRET_KEY: {EC2_SECRET_KEY}
            EC2_PRIVATE_KEY_FILE_PATH: ~/.cloudmesh/aws_cert.pem
            EC2_PRIVATE_KEY_FILE_NAME: aws_cert
    """

    # TODO: change to what you see in boto dicts the next values are from
    #  openstack which you must change


    output = {

        "vm": {  # updted for aws
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.cloud",
                      "instance_id",
                      "status",
                      "image",
                      "public_ips",
                      "private_ips",
                      "cm.creation_time",
                      "created",
                      "cm.kind"],
            "header": ["Name",
                       "Cloud",
                       "Instance ID",
                       "Status",
                       "Image",
                       "Public IPs",
                       "Private IPs",
                       "Creation Time",
                       "Started at",
                       "Kind"]
        },
        "image": {  # updated for aws
            "sort_keys": ["cm.name",
                          "State"],
            "order": ["cm.name",
                      "Architecture",
                      "ImageId",
                      "State",
                      "Hypervisor",
                      "VirtualizationType"],
            "header": ["Name",
                       "Architecture",
                       "ID",
                       "State",
                       "Hypervisor",
                       "VirtualizationType"]
        },
        "flavor": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "attributes.instanceType",
                      "price.pricePerUnit.USD",
                      "attributes.instanceFamily",
                      "attributes.vcpu",
                      "attributes.memory",
                      "attributes.storage",
                      "attributes.physicalProcessor",
                      "attributes.networkPerformance"],
            "header": ["ID",
                       "Name",
                       "Price",
                       "Family",
                       "VCPUS",
                       "RAM",
                       "Disk",
                       "Processor",
                       "Network"]
        },
        "key": {
            "sort_keys": ["name"],
            "order": ["name",
                      "type",
                      "format",
                      "fingerprint",
                      "comment"],
            "header": ["Name",
                       "Type",
                       "Format",
                       "Fingerprint",
                       "Comment"]
        },
        "secrule": {
            "sort_keys": ["name"],
            "order": ["name",
                      "direction",
                      "ethertype",
                      "ToPort",
                      "FromPort",
                      "IpProtocol",
                      "ipRange",
                      "groupId"
                      ],
            "header": ["Name",
                       "Direction",
                       "Ethertype",
                       "Port range max",
                       "Port range min",
                       "Protocol",
                       "Range",
                       "Remote group id"]
        },
        "secgroup": {
            "sort_keys": ["name"],
            "order": ["name",
                      "tags",
                      "direction",
                      "ethertype",
                      "ToPort",
                      "FromPort",
                      "IpProtocol",
                      "IpRanges",
                      "UserIdGroupPairs"
                      ],
            "header": ["Name",
                       "Tags",
                       "Direction",
                       "Ethertype",
                       "Port range max",
                       "Port range min",
                       "Protocol",
                       "Range",
                       "Remote group id"]
        }
    }

    # noinspection PyPep8Naming
    def Print(self, data, output, kind):

        if output == "table":

            order = self.output[kind]['order']
            header = self.output[kind]['header']

            print(Printer.flatwrite(data,
                                    sort_keys=["name"],
                                    order=order,
                                    header=header,
                                    output=output, )
                  )
        else:
            print(Printer.write(data, output=output))

    def find(self, elements, name=None):
        for element in elements:
            if element["name"] == name or element["cm"]["name"] == name:
                return element
        return None

    def list_secgroups(self, name=None):
        """
        List the named security groups

        :param name: Name of the security group. If not provided, returns all security group
        :return: List of dict
        """
        response = {}
        try:
            if name is None:
                response = self.ec2_client.describe_security_groups()
            else:
                response = self.ec2_client.describe_security_groups(
                    GroupNames=[name])
        except ClientError as e:
            Console.info("Security group doesn't exist")
        if response:
            return response['SecurityGroups']

    def list_secgroup_rules(self, name=None):

        """
        List the named security group

        :param name: The name of the group, if None all will be returned
        :return: returns list of dict
        """
        if name is None:
            name = 'default'
        sec_group_desc = self.list_secgroups(name)
        sec_group_rule = sec_group_desc[0]['IpPermissionsEgress']
        return sec_group_rule

    @staticmethod
    def _is_group_name_valid(name=None):
        not_valid = True
        if len(name) == 255:
            not_valid = False
        if name[0:3] == "sg-":
            not_valid = False
        return not_valid

    def add_secgroup(self, name=None, description=None):

        """
        Adds named security group

        :param name: Adds security group
        :param description: name = name of the security group to be added/created
                            description: Description of the security group. If its none then default description
                                         is added with user name and time of creation
        :return: None
        """

        response = self.ec2_client.describe_vpcs()
        vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')
        if description is None:
            description = f'security group crated at {str(datetime.utcnow())} by {self.user}'
        if self._is_group_name_valid(name):
            try:
                response = self.ec2_client.create_security_group(GroupName=name,
                                                                 Description=description,
                                                                 VpcId=vpc_id)
                security_group_id = response['GroupId']
                Console.ok(
                    f'Security Group Created {security_group_id} in vpc{vpc_id}')

            except ClientError as e:
                Console.info("Security group can't be added")

    def add_secgroup_rule(self,
                          name=None,  # group name
                          port=None,
                          protocol=None,
                          ip_range=None):
        """
        Add rule to named security group

        :param name: Name of the security group to which rfule needs to be added
        :param port: The start and end port range for the TCP and UDP protocols
        :param protocol:
        :param ip_range:
        :return:
        """

        try:
            portmin, portmax = port.split(":")
        except ValueError:
            portmin = -1
            portmax = -1

        try:
            data = self.ec2_client.authorize_security_group_ingress(
                GroupName=name,
                IpPermissions=[
                    {'IpProtocol': protocol,
                     'FromPort': int(portmin),
                     'ToPort': int(portmax),
                     'IpRanges': [{'CidrIp': ip_range}]},
                ])
            Console.ok(f'Ingress Successfully Set as {data}')
        except ClientError as e:
            Console.info("Rule couldn't be added to security group")

    def remove_secgroup(self, name=None):
        try:
            response = self.ec2_client.delete_security_group(GroupName=name)
            VERBOSE(response)
        except ClientError as e:
            Console.info(
                "Security group couldn't be removed as it doesn't exist")

    def upload_secgroup(self, name=None):

        if name is None:
            raise ValueError("name is None")
        group_exists = False
        sec_group = self.list_secgroups(name)

        if sec_group is None:
            return

        if len(sec_group) > 0:
            print("Warning group already exists")
            group_exists = True
        groups = Secgroup().list()
        rules = SecgroupRule().list()

        VERBOSE(rules)
        data = {}
        for rule in rules:
            data[rule['name']] = rule

        VERBOSE(groups)

        for group in groups:
            if group['name'] == name:
                break
        print("upload group:", name)

        if not group_exists:
            self.add_secgroup(name=name, description=group['description'])

            for r in group['rules']:
                found = data[r]
                print("    ", "rule:", found['name'])
                self.add_secgroup_rule(
                    name=name,
                    port=found["ports"],
                    protocol=found["protocol"],
                    ip_range=found["ip_range"])

        else:

            for r in group['rules']:
                found = data[r]
                print("    ", "rule:", found['name'])
                self.add_rules_to_secgroup(
                    name=name,
                    rules=[found])

    def add_rules_to_secgroup(self, name=None, rules=None):

        if name is None and rules is None:
            raise ValueError("name or rules are None")

        sec_group = self.list_secgroups(name)

        if len(sec_group) == 0:
            raise ValueError("group does not exist")

        for rule in rules:
            try:
                self.add_secgroup_rule(name=name,
                                       port=rule['ports'],
                                       protocol=rule['protocol'],
                                       ip_range=rule['ip_range'])
            except ClientError as e:
                Console.error(e)

    def remove_rules_from_secgroup(self, name=None, rules=None):

        if name is None and rules is None:
            raise ValueError("name or rules are None")

        sec_group = self.list_secgroups(name)
        if len(sec_group) == 0:
            raise ValueError("group does not exist")
        sec_group_rules = DictList(self.list_secgroup_rules(name))
        VERBOSE(sec_group_rules)

        '''
            To do match rules with each sec_group_rules and if found remove it as below
            Values below like protocol, portmin etc. are just default as of now
        '''

        try:
            data = self.ec2_client.revoke_security_group_ingress(
                GroupName=name,
                IpPermissions=[
                    {'IpProtocol': 'protocol',
                     'FromPort': 'portmin',
                     'ToPort': 'portmax',
                     'IpRanges': [{'CidrIp': 'ip_range'}]},
                ])
            Console.ok(f'Ingress Successfully Set as {data}')
        except ClientError as e:
            Console.error(e)

    def set_server_metadata(self, name, data):
        """
        :param name: virtual machine name
        :param m: cm dict
        :return:
        """
        #  {'cm': {'flavor': 't2.micro',
        #         'image': 'ami-0f65671a86f061fcd',
        #         'kind': 'vm',
        #         'name': 'test-vafandal-vm-128',
        #         'status': 'BOOTING',
        #         'user': 'vafandal'}}

        # data = {'cm': str(m)}
        # metadata = [ {'Key': 'cm.image', 'Value': image},
        #              {'Key': 'cm.name' , 'Value':name} ,
        #              {'Key': 'cm.flavor' , 'Value':size } ,
        #              {'Key': 'cm.user', 'Value':self.user} ,
        #              {'Key': 'cm.kind', 'Value':  "vm"} ,
        #              {'Key': 'cm.status', 'Value': "BOOTING"}
        #              ]
        id = self.info(name=name)['InstanceId']
        cm = self.get_server_metadata(name=name)
        cm.update(data)
        metadata = []
        for key, value in cm['cm'].items():
            metadata.append({'Key': f'cm.{key}', 'Value': value})
        response = self.ec2_client.create_tags(
            Resources=[
                id,
            ],
            Tags=metadata
        )
        return response

    def get_server_metadata_tags(self, name):
        """
        Describes the metadata tag of EC2 resource
        :param name: Virtual machine name

        :return: Dictionary with Metadata information
        """

        #   'Tags': [{'Key': 'cm.image', 'Value': 'ami-0f65671a86f061fcd'},
        #            {'Key': 'cm.kind', 'Value': 'vm'},
        #            {'Key': 'cm.user', 'Value': 'vafandal'},
        #            {'Key': 'cm.flavor', 'Value': 't2.micro'},
        #            {'Key': 'cm.status', 'Value': 'BOOTING'},
        #            {'Key': 'cm.name', 'Value': 'test-vafandal-vm-118'}],

        if name is None:
            Console.error("Please provide node name...")
            return

        instance_info = self.ec2_client.describe_instances(
            Filters=[
                {'Name': 'tag:cm.name', 'Values': [name]}
            ]
        )
        data = instance_info['Reservations'][0]['Instances'][0]
        return data['Tags']

    def get_server_metadata(self, name):
        """
        Describes the metadata tag of EC2 resource
        :param name: Virtual machine name

        :return: Dictionary with Metadata information
        """

        #   'Tags': [{'Key': 'cm.image', 'Value': 'ami-0f65671a86f061fcd'},
        #            {'Key': 'cm.kind', 'Value': 'vm'},
        #            {'Key': 'cm.user', 'Value': 'vafandal'},
        #            {'Key': 'cm.flavor', 'Value': 't2.micro'},
        #            {'Key': 'cm.status', 'Value': 'BOOTING'},
        #            {'Key': 'cm.name', 'Value': 'test-vafandal-vm-118'}],

        if name is None:
            Console.error("Please provide node name...")
            return

        instance_info = self.ec2_client.describe_instances(
            Filters=[
                {'Name': 'tag:cm.name', 'Values': [name]}
            ]
        )
        data = instance_info['Reservations'][0]['Instances'][0]
        metadata = {'cm': {}}
        for dat in data['Tags']:
            if 'cm.' in dat['Key']:
                key = dat['Key'].split('cm.')[1]
                value = dat['Value']
                metadata['cm'][key] = value
        return metadata

    def list_public_ips(self,
                        ip=None,
                        available=False):

        addresses = self.ec2_client.describe_addresses()
        ip_list = [address.get('PublicIp') for address in
                   addresses.get('Addresses')
                   if 'AssociationId' not in address]
        return ip_list[0]

    # release the ip
    def delete_public_ip(self, ip=None):

        ip_description = self._get_allocation_ids(self.ec2_client, ip)
        if not ip_description:
            return
        try:
            response = self.ec2_client.release_address(
                AllocationId=ip_description.get('AllocationId'),
            )
        except ClientError as e:
            Console.error(e)
        VERBOSE(f'Public IP {ip} deleted')
        return response

    def create_public_ip(self):
        try:
            response = self.ec2_client.allocate_address(
                Domain='vpc'
            )
        except ClientError as e:
            Console.error(e)

        return response

    def find_available_public_ip(self):
        addresses = self.ec2_client.describe_addresses()
        public_ips = [address['PublicIp'] for address in
                      addresses.get('Addresses')]
        VERBOSE(public_ips)
        return public_ips

    @staticmethod
    def _get_allocation_ids(client, ip):

        try:
            addresses = client.describe_addresses(PublicIps=[ip])
            ip_description = addresses.get('Addresses')[0]
            return ip_description
        except ClientError as e:
            Console.error(e)

    def attach_public_ip(self, node, ip):

        instances = self._get_instance_id(self.ec2_resource, node)
        instance_id = []
        for each_instance in instances:
            instance_id.append(each_instance.instance_id)
        if not instance_id:
            raise ValueError("Invalid instance name provided...")
        if ip not in self.find_available_public_ip():
            raise ValueError("IP address is not in pool")

        try:
            response = self.ec2_client.associate_address(
                AllocationId=self._get_allocation_ids(self.ec2_client, ip).get(
                    'AllocationId'),
                InstanceId=instance_id[0],
                AllowReassociation=True,
            )
        except ClientError as e:
            Console.error(e)
        return response

    def detach_public_ip(self, node, ip):

        instances = self._get_instance_id(self.ec2_resource, node)
        instance_id = []
        for each_instance in instances:
            instance_id.append(each_instance.instance_id)
        if not instance_id:
            raise ValueError("Invalid instance name provided...")
        if ip not in self.find_available_public_ip():
            raise ValueError("IP address is not in pool")
        try:
            response = self.ec2_client.disassociate_address(
                AssociationId=self._get_allocation_ids(self.ec2_client, ip).get(
                    'AssociationId'),
            )
        except ClientError as e:
            Console.error(e)
        Console.msg(response)

    def wait(self,
             vm=None,
             interval=None,
             timeout=None):
        if interval is None:
            # if interval is too low, OS will block your ip
            interval = 5
        if timeout is None:
            timeout = 360
        # instance_id = vm['instance_id']
        Console.info(
            f"waiting for instance to be reachable: Interval: {interval}, Timeout: {timeout}")
        timer = 0
        while timer < timeout:
            try:
                r = self.ssh(vm=vm, command='echo IAmReady').strip()
                if 'IAmReady' in r:
                    return True
            except:
                pass
            sleep(interval)
            timer += interval
        return False

    def ssh(self, vm=None, command=None):

        def key_selector(keys):
            '''
           This is a helper method for ssh key selection
           THIS IS JUST A SAFETY MEASURE, PLEASE DON'T MIND IT
            :param keys:
            :return:
            '''
            tmp_keys = keys[:]
            # indices = range(1,len(tmp_keys)+1)
            for key_idx, key in enumerate(keys):
                key['idx'] = key_idx + 1
            print(Printer.flatwrite(tmp_keys,
                                    sort_keys=["idx"],
                                    order=['idx', 'KeyName', 'KeyFingerprint'],
                                    header=['Index', 'Key Name',
                                            "Key Fingerprint"],
                                    output="table",
                                    humanize=None)
                  )
            # Console.msg("Please select one of the AWS key indices from the table above: ")
            picked = 0
            while picked < 1 or picked > len(keys):
                try:
                    picked = int(input(
                        "Please select one of the AWS key indices from the table above: "))
                except ValueError:
                    pass
            return keys[picked - 1]

        cm = CmDatabase()
        ip = vm['public_ips']

        try:
            key_name = vm['KeyName']
            keys = cm.find_all_by_name(name=key_name, kind="key")
            for k in keys:
                if 'location' in k.keys():
                    if 'private' in k['location'].keys():
                        key = k['location']['private']
                        break

        except (KeyError, IndexError):
            aws_keys = cm.find(kind='key', cloud='aws')
            if len(aws_keys) == 0:
                Console.error(
                    f"Could not find a key for the AWS instance '{vm['name']}'")
                Console.error(
                    f"Use `cms help key` to learn how to add and upload a key for AWS")
                return
            aws_key = key_selector(aws_keys)
            for sshkey in cm.find_all_by_name(name=aws_key['KeyName'],
                                              kind="key"):
                if "location" in sshkey.keys():
                    key = sshkey['location']['private']
                    break
        user = "ubuntu"  # needs to be set on creation.

        if command is None:
            command = ""

        if user is None:
            location = ip
        else:
            location = user + '@' + ip
        cmd = "ssh " \
              "-o StrictHostKeyChecking=no " \
              "-o UserKnownHostsFile=/dev/null " \
              f"-i {key} {location} {command}"
        cmd = cmd.strip()
        print(cmd)
        # VERBOSE(cmd)

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
                    ssh = subprocess.Popen(cmd,
                                           shell=True,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
            else:
                ssh = subprocess.Popen(cmd,
                                       shell=True,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            result = ssh.stdout.read().decode("utf-8")
            if not result:
                error = ssh.stderr.readlines()
                print("ERROR: %s" % error)
            else:
                return result

    def __init__(self, name=None, configuration="~/.cloudmesh/cloudmesh.yaml"):
        """
        Initializes the provider. The default parameters are read from the
        configuration file that is defined in yaml format.

        :param name: The name of the provider as defined in the yaml file
        :param configuration: The location of the yaml configuration file
        """

        self.conf = Config(configuration)["cloudmesh"]
        super().__init__(name, self.conf)

        self.user = Config()["cloudmesh"]["profile"]["user"]
        self.spec = self.conf["cloud"][name]
        self.cloud = name

        self.default = self.spec["default"]
        self.cloudtype = self.spec["cm"]["kind"]

        self.cred = self.spec["credentials"]

        credentials = self.cred

        self.access_id = credentials['EC2_ACCESS_ID']
        self.secret_key = credentials['EC2_SECRET_KEY']
        self.account_id = self._get_account_id()
        self.region = credentials['region']
        self.session = None

        self.instance_id = None
        if self.session is None:
            self.session = boto3.Session(aws_access_key_id=self.access_id,
                                         aws_secret_access_key=self.secret_key,
                                         region_name=self.region)
        if self.session is None:
            Console.error("Invalid credentials...")
            return
        self.ec2_resource = self.session.resource('ec2')
        self.ec2_client = self.ec2_resource.meta.client

    @staticmethod
    def _get_instance_id(ec2_resource, name):

        instances = ec2_resource.instances.filter(Filters=[
            {'Name': 'tag:cm.name',
             'Values': [name]
             }
        ]
        )
        print(instances)
        return instances

    def start(self, name=None):

        """
        start a node

        :param name: the unique instance name

        :return:  The dict representing the node
        """
        instances = self._get_instance_id(self.ec2_resource, name)

        for each_instance in instances:
            try:
                self.ec2_client.start_instances(
                    InstanceIds=[each_instance.instance_id])

                self.add_server_metadata(name=name, tags=[
                    {'Key': 'cm.status', 'Value': "ACTIVE"}])
            except ClientError:
                Console.error(
                    "Currently instance cant be started...Please try again")
            Console.msg("Starting Instance..Please wait...")
            waiter = self.ec2_client.get_waiter('instance_running')
            waiter.wait(Filters=[
                {'Name': 'instance-id', 'Values': [each_instance.instance_id]}])
            Console.ok(
                f"Instance having Tag:{name} and "
                f"Instance-Id:{each_instance.instance_id} started")

    def stop(self, name=None, hibernate=False):

        """
        stops the node with the given name

        :param name: the instance name
        :param hibernate: stop or hibernate

        :return: The dict representing the node including updated status
        """

        if name is None:
            Console.error("Please provide instance id...")
            return
        instances = self._get_instance_id(self.ec2_resource, name)

        for each_instance in instances:
            try:
                self.ec2_client.stop_instances(
                    InstanceIds=[each_instance.instance_id],
                    Hibernate=hibernate)

                self.add_server_metadata(name=name, tags=[
                    {'Key': 'cm.status', 'Value': "STOPPED"}])
            except ClientError:
                Console.error(
                    "Currently instance cant be stopped...Please try again")
            Console.msg("Stopping Instance..Please wait...")
            waiter = self.ec2_client.get_waiter('instance_stopped')
            waiter.wait(Filters=[
                {'Name': 'instance-id', 'Values': [each_instance.instance_id]}])
            Console.ok(
                f"Instance having Tag:{name} and "
                "Instance-Id:{each_instance.instance_id} stopped")

    def info(self, name=None):

        """
        gets the information of a node with a given name

        :param name: the  node name

        :return: The dict representing the node including updated status
        """
        if name is None:
            Console.error("Please provide node name...")
            return

        instance_info = self.ec2_client.describe_instances(
            Filters=[
                {'Name': 'tag:cm.name', 'Values': [name]}
            ]
        )
        data = {}
        if (len(instance_info['Reservations']) > 0):
            data = instance_info['Reservations'][0]['Instances'][0]
            # TODO: this needs to be fixed :
            data['name'] = name
            data['status'] = data['State']['Name']
            data.update(self.get_server_metadata(name))
        return data

    def instance_is_reachable(self, instance_id=None):
        '''
        gets the information of a statuso of a VM with a given name, useful for when you want to check if the vm is ready for ssh
        Note: describe_instance_status doesn't filter by tag , so we should use instance ID
        :param name: name
        :return:
        '''

        # example output:
        # {'InstanceStatuses': [{'AvailabilityZone': 'us-east-2b',
        #                        'InstanceId': 'i-0014150545f9da2ac',
        #                        'InstanceState': {'Code': 16, 'Name': 'running'},
        #                        'InstanceStatus': {'Details': [{'Name': 'reachability',
        #                                                        'Status': 'passed'}],
        #                                           'Status': 'ok'},
        #                        'SystemStatus': {'Details': [{'Name': 'reachability', 'Status': 'passed'}],
        #                                         'Status': 'ok'}}],
        #  'ResponseMetadata': {'RequestId': 'a3161eab-386e-482c-873f-c12984262fd5',
        #                       'HTTPStatusCode': 200,
        #                       'HTTPHeaders': {'content-type': 'text/xml;charset=UTF-8',
        #                                       'content-length': '1139',
        #                                       'date': 'Fri, 20 Sep 2019 17:42:43 GMT',
        #                                       'server': 'AmazonEC2'},
        #                       'RetryAttempts': 0}}

        # The Instance Reachability check confirms that we are able to deliver network packets to the operating system hosted on your instance.
        #
        # The System Reachability check confirms that we are able to get network packets to your instance.

        if instance_id is None:
            Console.error("Please provide instance_id ...")
            return
        if type(instance_id) != list:
            instance_id = [instance_id]
        instance_status = \
            self.ec2_client.describe_instance_status(InstanceIds=instance_id)[
                'InstanceStatuses']
        if (len(instance_status) > 0):
            status = instance_status[0]['InstanceStatus']['Details'][0][
                'Status']
            if status.lower() == 'passed':
                return True
        return False

    def list(self):

        """
        list all nodes id

        :return: an array of dicts representing the nodes
        'instance_tag': each_instance.tags[0]['Name']
        """
        instance_ids = []
        for each_instance in self.ec2_resource.instances.all():

            # print(each_instance.tags)
            if len(each_instance.tags) > 0:
                name = [tag['Value'] for tag in each_instance.tags if
                        tag['Key'] == 'Name'][0]
            else:
                name = ''
            instance_ids.append({
                'kind': 'aws',
                'KeyName': each_instance.key_name,
                'status': each_instance.state['Name'],
                'created': each_instance.launch_time.strftime(
                    "%m/%d/%Y, %H:%M:%S") if each_instance.launch_time else '',
                'updated': each_instance.launch_time.strftime(
                    "%m/%d/%Y, %H:%M:%S") if each_instance.launch_time else '',
                # 'name': each_instance.tags[0]['Value'] if each_instance.tags else '',
                'name': name,
                'instance_id': each_instance.id,
                'instance_tag': each_instance.tags[0][
                    'Value'] if each_instance.tags else '',
                'image': each_instance.image_id,
                'public_ips': each_instance.public_ip_address,
                'private_ips': each_instance.private_ip_address
            })
        # return instance_ids
        return self.update_dict(instance_ids, kind="vm")

    def suspend(self, name=None):

        """
        suspends the node with the given name

        :param name: the name of the node

        :return: The dict representing the node
        """
        return self.stop(name=name, hibernate=True)

    def resume(self, name=None):

        """
        resume the named node

        :param name: the name of the node

        :return: the dict of the node
        """
        instances = self._get_instance_id(self.ec2_resource, name)

        for each_instance in instances:
            instance = self.ec2_resource.Instance(each_instance.instance_id)
            instance.reboot()
            Console.msg("Rebooting Instance..Please wait...")
            Console.ok(
                f"Instance having Tag:{name} and "
                "Instance-Id:{each_instance.instance_id} rebooted")

    def destroy(self, name=None):

        """
        Destroys the node
        :param name: the name of the node

        :return: the dict of the node
        """
        instances = self._get_instance_id(self.ec2_resource, name)

        for each_instance in instances:
            try:
                # self.ec2_resource.create_tags(Resources = [each_instance.instance_id],
                #                               Tags=[{'Key': 'cm.status', 'Value': "Terminated"}])
                self.ec2_client.terminate_instances(
                    InstanceIds=[each_instance.instance_id], )

                self.add_server_metadata(name=name, tags=[
                    {'Key': 'cm.status', 'Value': "TERMINATED"}])
            except ClientError:
                Console.error(
                    "Currently instance cant be terminated...Please try again")
            Console.msg("Terminating Instance..Please wait...")
            waiter = self.ec2_client.get_waiter('instance_terminated')
            waiter.wait(Filters=[
                {'Name': 'instance-id', 'Values': [each_instance.instance_id]}])
            Console.ok(
                f"Instance having Tag:{name} and "
                f"Instance-Id:{each_instance.instance_id} terminated")

    def create(self,
               name=None,
               image=None,
               size=None,
               location=None,
               timeout=360,
               key=None,
               secgroup=None,
               ip=None,
               user=None,
               public=None,
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

        :return: the list with the modified dicts
        """
        """
        create one node
        """
        if not ip and public:
            ip = self.find_available_public_ip()
        elif ip is not None:
            entry = self.list_public_ips(ip=ip, available=True)
            if len(entry) == 0:
                Console.error("ip not available")
            return None

        banner("Create Server")
        Console.msg(f"    Name:     {name}")
        Console.msg(f"    User:     {user}")
        Console.msg(f"    IP:       {ip}")
        Console.msg(f"    Image:    {image}")
        Console.msg(f"    Size:     {size}")
        Console.msg(f"    Public:   {public}")
        Console.msg(f"    Key:      {key}")
        Console.msg(f"    Location: {location}")
        Console.msg(f"    Timeout:  {timeout}")
        Console.msg(f"    Secgroup: {secgroup}")
        Console.msg(f"    Group:    {group}")
        # Console.msg(f"    Groups:   {groups}")
        Console.msg("")

        if secgroup is None:
            secgroup = 'default'

        if key is None:
            raise ValueError("Key must be set. Use cms set key=<key name>")

        #
        # BUG: the tags seem incomplete
        #
        if metadata is None:
            metadata = []
        metadata = [{'Key': 'cm.image', 'Value': image},
                    {'Key': 'cm.name', 'Value': name},
                    {'Key': 'cm.flavor', 'Value': size},
                    {'Key': 'cm.user', 'Value': self.user},
                    {'Key': 'cm.kind', 'Value': "vm"},
                    {'Key': 'cm.status', 'Value': "BOOTING"},
                    {'Key': 'Name', 'Value': name}
                    ]
        # VERBOSE(metadata)
        new_ec2_instance = self.ec2_resource.create_instances(
            ImageId=image,
            InstanceType=size,
            MaxCount=1,
            MinCount=1,
            SecurityGroups=[secgroup],
            KeyName=key,
            TagSpecifications=[{'ResourceType': 'instance',
                                'Tags': metadata}]
        )
        # VERBOSE(new_ec2_instance)
        new_ec2_instance = new_ec2_instance[0]
        waiter = self.ec2_client.get_waiter('instance_exists')

        waiter.wait(Filters=[{'Name': 'instance-id',
                              'Values': [new_ec2_instance.instance_id]}],
                    WaiterConfig={
                        'Delay': 20,
                        'MaxAttempts': timeout / 20
                    }
                    )
        print()
        Console.ok("Instance created...")
        print()
        # if IP provided, Attach it to new instance
        if ip:
            self.attach_public_ip(name, ip)
        # x = self.ec2_client.describe_instances(InstanceIds=[new_ec2_instance.instance_id])
        # VERBOSE(x)
        data = self.info(name=name)

        # VERBOSE(data)
        data['name'] = name
        data['kind'] = 'aws'
        data['status'] = new_ec2_instance.state['Name'],
        data['created'] = new_ec2_instance.launch_time.strftime(
            "%m/%d/%Y, %H:%M:%S") if new_ec2_instance.launch_time else '',
        data['updated'] = new_ec2_instance.launch_time.strftime(
            "%m/%d/%Y, %H:%M:%S") if new_ec2_instance.launch_time else '',
        data['name'] = new_ec2_instance.tags[0][
                           'Value'] if new_ec2_instance.tags else '',
        data['instance_id'] = new_ec2_instance.id,
        data['image'] = new_ec2_instance.image_id,
        data['key_name'] = key,
        Console.msg("Waiting for the Public IP address assignment ...")
        while True:
            try:
                public_ip = \
                    self.ec2_client.describe_instances(
                        InstanceIds=[new_ec2_instance.id])['Reservations'][0][
                        'Instances'] \
                        [0]['PublicIpAddress'],
                break
            except KeyError:
                time.sleep(0.5)
        data['public_ips'] = public_ip[0]
        data['private_ips'] = new_ec2_instance.private_ip_address

        Console.msg(f"    Public IP:   {data['public_ips']}")
        Console.msg(f"    Private IP:  {data['private_ips']}")

        output = self.update_dict(data, kind="vm")[0]
        return output

    def rename(self, name=None, destination=None):

        """
        rename a node

        :param destination: the destination name
        :param name: the current name

        :return: the dict with the new name
        """
        # if destination is None, increase the name counter and use the new name
        instances = self._get_instance_id(self.ec2_resource, name)
        tag_response = None
        for each_instance in instances:
            tag_response = self.ec2_client.create_tags(
                Resources=[each_instance.instance_id],
                Tags=[{
                    'Key': 'Name',
                    'Value': destination
                }]
            )
        return tag_response

    def keys(self):

        """
        Lists the keys on the cloud

        :return: dict
        """
        keys = self.ec2_client.describe_key_pairs()['KeyPairs']
        data = self.update_dict(keys, kind="key")
        return data

    def key_upload(self, key=None):

        # The gey is stored in the database, we do not create a new keypair,
        # we upload our local key to aws
        # BUG name=None, wrong?
        # ~/.ssh/id_rsa.pub

        """
        uploads the key specified in the yaml configuration to the cloud
        :param key
        :return: the dict of the key
        """
        key_name = key["name"]
        cloud = self.cloud
        Console.msg(f"uploading the key: {key_name} -> {cloud}")
        try:
            r = self.ec2_client.import_key_pair(KeyName=key_name,
                                                PublicKeyMaterial=key[
                                                    'public_key'])
        except ClientError as e:
            # Console.error("Key already exists")
            VERBOSE(e)
            raise ValueError  # this is raised because key.py catches valueerror
        return r

    def key_delete(self, name=None):

        """
        deletes the key with the given name

        :param name: The name of the key

        :return: the dict of the key
        """
        cloud = self.cloud
        Console.msg(f"deleting the key: {name} -> {cloud}")
        r = self.ec2_client.delete_key_pair(KeyName=name)
        return r

    def add_server_metadata(self, name, tags):
        """
        Add or Update tag to metadata

        :param name: name of the fm
        :param tags: tags to be added to vm metadata

        :return: the dict of the metadata
        """

        if name is None:
            Console.error("Please provide node name...")
            return

        instances = self._get_instance_id(self.ec2_resource, name)
        response = None
        for each_instance in instances:
            try:
                response = self.ec2_client.create_tags(
                    Resources=[each_instance.instance_id],
                    Tags=tags)
            except ClientError:
                Console.error(
                    "Currently metadata cant not be added or updated...Please try again")
        return response

    def delete_server_metadata(self, name, tags=None):
        """
        gets the metadata for the server

        :param name: name of the vm
        :param tags: tags to be deleted from vm metadata

        :return: the dict of the metadata
        """

        if name is None:
            Console.error("Please provide node name...")
            return

        instances = self._get_instance_id(self.ec2_resource, name)

        if tags is None:
            tags = self.get_server_metadata_tags(name=name)
        response = None
        for each_instance in instances:
            try:
                response = self.ec2_client.delete_tags(
                    Resources=[each_instance.instance_id],
                    Tags=tags)
            except ClientError:
                Console.error(
                    "Currently metadata cant not be deleted...Please try again")
        return response

    def _get_account_id(self):
        '''
        retrieves the acount id which is used to find the images of the current account
        :return:
        '''
        client = boto3.client("sts", aws_access_key_id=self.access_id,
                              aws_secret_access_key=self.secret_key)
        return client.get_caller_identity()["Account"]

    def images(self, **kwargs):

        """
        Lists the images on the cloud

        :return: the dict of the images
        """
        Console.msg(
            f"Getting the list of images for {self.cloud} cloud, this might take a few minutes ...")
        images = self.ec2_client.describe_images()
        Console.ok(f"Images list for {self.cloud} cloud retrieved successfully")
        data = self.update_dict(images['Images'], kind="image")
        self.get_images_and_import(data)

    @DatabaseImportAsJson()
    def get_images_and_import(self, data):
        '''
        this is a helper function for images() to allow the images to be passed and saved to the database with
        databaseimportasjson() decorator instead of the regular databaseupdate() decorator.
        :param data:
        :return:
        '''
        return {'db': 'cloudmesh', 'collection': 'aws-image', 'data': data}

    def image(self, name=None):

        """
        Gets the image with a given nmae

        :param name: The name of the image

        :return: the dict of the image
        """
        cm = CmDatabase()
        return cm.find_name(name, kind='image')

    def flavors(self, **kwargs):

        """
        Lists the flavors on the cloud

        :return: dict of flavors
        """
        flavors = AwsFlavor(session = self.session)
        data = flavors.fetch()
        result = flavors.list(data)
        return self.update_dict(result, kind="flavor")

    def flavor(self, name=None):

        """
        Gets the flavor with a given name
        :param name: The name of the flavor
        :return: The dict of the flavor
        """
        flavors = AwsFlavor()
        flavors.update()
        for flavor in flavors.get():
            if flavor['name'] == name:
                return [flavor]
        return []

    def update_dict(self, elements, kind=None):

        """
        This function adds a cloudmesh cm dict to each dict in the list
        elements.
        Libcloud
        returns an object or list of objects With the dict method
        this object is converted to a dict. Typically this method is used
        internally.

        :param elements: the list of original dicts. If elements is a single
                         dict a list with a single element is returned.
        :param kind: for some kinds special attributes are added. This includes
                     key, vm, image, flavor.
        :return: The list with the modified dicts
        """
        if elements is None:
            return None
        elif type(elements) == list:
            _elements = elements
        else:
            _elements = [elements]

        d = []
        for entry in _elements:

            if kind == 'key':

                entry['comment'] = "N/A"
                entry['name'] = entry['KeyName']
                entry['fingerprint'] = entry['KeyFingerprint']
                entry['type'] = 'N/A'
                entry['format'] = 'N/A'

                # amaozn doesn ot return the public_key, hence commenting
                # entry['format'] = \
                #     entry['public_key'].split(" ", 1)[0].replace("ssh-", "")
            elif kind == 'image':
                try:
                    entry['name'] = entry.pop('Name')
                except KeyError:
                    entry['name'] = 'N/A'
                    continue

            entry["cm"] = {
                "kind": kind,
                "driver": self.cloudtype,
                "cloud": self.cloud,
                "name": entry['name'],
                "updated": str(datetime.utcnow()),
            }
            if kind == 'vm':

                # This is clearly wrong

                # "Image": entry['image'],
                # "Public IPs": entry['public_ips'],
                # "Private IPs": entry['private_ips']

                if "created_at" in entry:
                    entry["cm"]["created"] = str(entry["created_at"])
                    # del entry["created_at"]
                else:
                    entry["cm"]["created"] = entry["cm"]["updated"]
            elif kind == 'flavor':
                entry["cm"]["created"] = entry["updated"] = str(
                    datetime.utcnow())

            elif kind == 'image':
                entry['cm']['created'] = str(datetime.utcnow())
                entry['cm']['updated'] = str(datetime.utcnow())

            d.append(entry)

        return d


if __name__ == "__main__":
    provider = Provider(name='aws')
