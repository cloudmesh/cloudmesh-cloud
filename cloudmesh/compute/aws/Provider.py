from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.configuration.Config import Config
from cloudmesh.provider import ComputeProviderPlugin
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common3.DictList import DictList
from cloudmesh.management.configuration.name import Name
from cloudmesh.common.util import banner


class Provider(ComputeNodeABC, ComputeProviderPlugin):
    kind = "aws"

    # TODO: change to what you see in boto dicts the next values are from
    #  openstack which you must change

    output = {

        "vm": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.cloud",
                      "vm_state",
                      "status",
                      "image",
                      "public_ips",
                      "private_ips",
                      "project_id",
                      "launched_at",
                      "cm.kind"],
            "header": ["Name",
                       "Cloud",
                       "State",
                       "Status",
                       "Image",
                       "Public IPs",
                       "Private IPs",
                       "Project ID",
                       "Started at",
                       "Kind"]
        },
        "image": {
            "sort_keys": ["cm.name",
                          "extra.minDisk"],
            "order": ["cm.name",
                      "size",
                      "min_disk",
                      "min_ram",
                      "status",
                      "cm.driver"],
            "header": ["Name",
                       "Size (Bytes)",
                       "MinDisk (GB)",
                       "MinRam (MB)",
                       "Status",
                       "Driver"]
        },
        "flavor": {
            "sort_keys": ["cm.name",
                          "vcpus",
                          "disk"],
            "order": ["cm.name",
                      "vcpus",
                      "ram",
                      "disk"],
            "header": ["Name",
                       "VCPUS",
                       "RAM",
                       "Disk"]
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
        "secgroup": {
            "sort_keys": ["name"],
            "order": ["name",
                      "tags",
                      "direction",
                      "ethertype",
                      "port_range_max",
                      "port_range_min",
                      "protocol",
                      "remote_ip_prefix",
                      "remote_group_id"
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

    # TODO: look at the openstack provider and ComputeNodeABC to see which
    #  methods you must have. In openstack i created some convenience classes
    #  to make things easier
    #  start with a prg in this dir similar to ../openstack/os_sdk.py, call it
    #  aws_boto.py, make sure to use Config()

    # noinspection PyPep8Naming
    def Print(self, output, kind, data):
        raise NotImplementedError

    def find(self, elements, name=None):
        # TODO: Vafa
        raise NotImplementedError

    def list_secgroups(self, name=None):
        try:
            if name is None:
                response = self.ec2_client.describe_security_groups()
            else:
                response = self.ec2_client.describe_security_groups(GroupNames=[name])
        except ClientError as e:
            print(e)
        VERBOSE(response)
        return response

    def list_secgroup_rules(self, name='default'):

        sec_group_desc = self.list_secgroups(name)
        sec_group_rule = sec_group_desc['IpPermissions']
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
                print(f'Security Group Created {security_group_id} in vpc{vpc_id}')

            except ClientError as e:
                print(e)

    def add_secgroup_rule(self,
                          name=None,  # group name
                          port=None,
                          protocol=None,
                          ip_range=None):
        try:
            portmin, portmax = port.split(":")
        except ValueError:
            portmin = None
            portmax = None

        try:
            data = self.ec2_client.authorize_security_group_ingress(
                GroupName=name,
                IpPermissions=[
                    {'IpProtocol': protocol,
                     'FromPort': portmin,
                     'ToPort': portmax,
                     'IpRanges': [{'CidrIp': ip_range}]},
                ])
            print(f'Ingress Successfully Set as {data}')
        except ClientError as e:
            print(e)

    def remove_secgroup(self, name=None):
        try:
            response = self.ec2_client.delete_security_group(GroupName=name)
            VERBOSE(response)
        except ClientError as e:
            print(e)

    def upload_secgroup(self, name=None):
        # TODO: Vafa
        raise NotImplementedError

    def add_rules_to_secgroup(self, name=None, rules=None):
        # TODO: Vafa

        raise NotImplementedError

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
            print(f'Ingress Successfully Set as {data}')
        except ClientError as e:
            print(e)

    def set_server_metadata(self, name, m):
        """

        :param name: virtual machine name
        :param m: cm dict
        :return:
        """
        data = {'cm': str(m)}
        tag = self.ec2_resource.Tag('metadata', 'cm', data)
        VERBOSE(tag)

    def get_server_metadata(self, name):
        # TODO: Saurabh
        raise NotImplementedError

    # these are available to be associated
    def list_public_ips(self,
                        ip=None,
                        available=False):

        addresses = self.ec2_client.describe_addresses()
        ip_list = [address.get('PublicIp') for address in addresses.get('Addresses')
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
            print(e)
        VERBOSE(f'Public IP {ip} deleted')
        return response

    def create_public_ip(self):
        try:
            response = self.ec2_client.allocate_address(
                Domain='vpc'
            )
        except ClientError as e:
            print(e)

        return response

    def find_available_public_ip(self):
        addresses = self.ec2_client.describe_addresses()
        public_ips = [address['PublicIp'] for address in addresses.get('Addresses')]
        VERBOSE(public_ips)
        return public_ips

    @staticmethod
    def _get_allocation_ids(client, ip):

        try:
            addresses = client.describe_addresses(PublicIps=[ip])
            ip_description = addresses.get('Addresses')[0]
            return ip_description
        except ClientError as e:
            print(e)

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
                AllocationId=self._get_allocation_ids(self.ec2_client, ip).get('AllocationId'),
                InstanceId=instance_id[0],
                AllowReassociation=True,
            )
        except ClientError as e:
            print(e)
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
                AssociationId=self._get_allocation_ids(self.ec2_client, ip).get('AssociationId'),
            )
        except ClientError as e:
            print(e)
        print(response)

    # see the openstack example it will be almost the same as in openstack
    # other than getting
    # the ip and username
    def ssh(self, vm=None, command=None):
        # TODO: Vafa
        # Host.ssh ....
        raise NotImplementedError

    def __init__(self, name=None, configuration="~/.cloudmesh/cloudmesh.yaml"):
        """
        Initializes the provider. The default parameters are read from the
        configuration file that is defined in yaml format.

        :param name: The name of the provider as defined in the yaml file
        :param configuration: The location of the yaml configuration file
        """

        conf = Config(configuration)["cloudmesh"]
        super().__init__(name, conf)

        self.user = Config()["cloudmesh"]["profile"]["user"]
        self.spec = conf["cloud"][name]
        self.cloud = name

        self.default = self.spec["default"]
        self.cloudtype = self.spec["cm"]["kind"]

        self.cred = self.spec["credentials"]

        credentials = self.cred

        self.access_id = credentials['EC2_ACCESS_ID']
        self.secret_key = credentials['EC2_SECRET_KEY']
        self.region = credentials['region']
        self.session = None

        self.instance_id = None
        if self.session is None:
            self.session = boto3.Session(aws_access_key_id=self.access_id,
                                         aws_secret_access_key=self.secret_key,
                                         region_name=self.region)
        if self.session is None:
            print("Invalid credentials...")
            return
        self.ec2_resource = self.session.resource('ec2')
        self.ec2_client = self.ec2_resource.meta.client

    @staticmethod
    def _get_instance_id(ec2_resource, name):

        instances = ec2_resource.instances.filter(Filters=[
            {'Name': 'tag:Name',
             'Values': [name]
             }
        ]
        )

        return instances

    def start(self, name=None):
        # TODO: Sriman
        """
        start a node

        :param name: the unique node name
        :return:  The dict representing the node
        """
        instances = self._get_instance_id(self.ec2_resource, name)

        for each_instance in instances:
            try:
                self.ec2_client.start_instances(
                    InstanceIds=[each_instance.instance_id])
            except ClientError:
                print("Currently instance cant be started...Please try again")
            print("Starting Instance..Please wait...")
            waiter = self.ec2_client.get_waiter('instance_running')
            waiter.wait(Filters=[
                {'Name': 'instance-id', 'Values': [each_instance.instance_id]}])
            print(
                f"Instance having Tag:{name} and "
                f"Instance-Id:{each_instance.instance_id} started")

    def stop(self, name=None):
        # TODO: Sriman
        """
        stops the node with the given name

        :param name:
        :return: The dict representing the node including updated status
        """

        if name is None:
            print("Please provide instance id...")
            return
        instances = self._get_instance_id(self.ec2_resource, name)

        for each_instance in instances:
            try:
                self.ec2_client.stop_instances(
                    InstanceIds=[each_instance.instance_id])
            except ClientError:
                print("Currently instance cant be stopped...Please try again")
            print("Stopping Instance..Please wait...")
            waiter = self.ec2_client.get_waiter('instance_stopped')
            waiter.wait(Filters=[
                {'Name': 'instance-id', 'Values': [each_instance.instance_id]}])
            print(
                f"Instance having Tag:{name} and "
                "Instance-Id:{each_instance.instance_id} stopped")

    def info(self, name=None):
        # TODO: Sriman
        """
        gets the information of a node with a given name

        :param name:
        :return: The dict representing the node including updated status
        """
        if name is None:
            print("Please provide node name...")
            return

        instance_info = self.ec2_client.describe_instances(Filters=[
            {'Name': 'tag:Name',
             'Values': [name]
             }
        ])
        return instance_info

    def list(self):
        # TODO: Sriman
        """
        list all nodes id

        :return: an array of dicts representing the nodes
        'instance_tag': each_instance.tags[0]['Name']
        """
        instance_ids = []
        for each_instance in self.ec2_resource.instances.all():

            instance_ids.append({
                                 'kind' : 'aws',
                                 'status': each_instance.state['Name'],
                                 'created' : each_instance.launch_time.strftime("%m/%d/%Y, %H:%M:%S") if each_instance.launch_time else '',
                                 'updated' : each_instance.launch_time.strftime("%m/%d/%Y, %H:%M:%S") if each_instance.launch_time else '',
                                 'name': each_instance.tags[0]['Value'] if each_instance.tags else '',
                                 'instance_id': each_instance.id,
                                  'instance_tag': each_instance.tags[0]['Value'] if each_instance.tags else '',
                                 'image': each_instance.image_id,
                                 'public_ips' : each_instance.public_ip_address,
                                 'private_ips': each_instance.private_ip_address
                                 })
        #return instance_ids
        return self.update_dict(instance_ids, kind="vm")

    def suspend(self, name=None):
        # TODO: Sriman
        """
        suspends the node with the given name

        :param name: the name of the node
        :return: The dict representing the node
        """
        raise NotImplementedError

    def resume(self, name=None):
        # TODO: Sriman
        """
        resume the named node

        :param name: the name of the node
        :return: the dict of the node
        """
        instances = self._get_instance_id(self.ec2_resource, name)

        for each_instance in instances:
            instance = self.ec2_resource.Instance(each_instance.instance_id)
            instance.reboot()
            print("Rebooting Instance..Please wait...")
            print(
                f"Instance having Tag:{name} and "
                "Instance-Id:{each_instance.instance_id} rebooted")

    def destroy(self, name=None):
        # TODO: Sriman
        """
        Destroys the node
        :param name: the name of the node
        :return: the dict of the node
        """
        instances = self._get_instance_id(self.ec2_resource, name)

        for each_instance in instances:
            try:
                self.ec2_client.terminate_instances(
                    InstanceIds=[each_instance.instance_id])
            except ClientError:
                print(
                    "Currently instance cant be terminated...Please try again")
            print("Terminating Instance..Please wait...")
            waiter = self.ec2_client.get_waiter('instance_terminated')
            waiter.wait(Filters=[
                {'Name': 'instance-id', 'Values': [each_instance.instance_id]}])
            print(
                f"Instance having Tag:{name} and "
                f"Instance-Id:{each_instance.instance_id} terminated")

    #
    # i made some changes in openstack create, compare what i did with what
    # you did. Figure out how to pass metadata into the vm as we need the cm
    # dict passed as metadata to the vm
    # also all arguments must have the same name as in openstack/abc compute
    # class. I do not think we used keyname, we used key_name=key,
    #
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

        # TODO: Sriman
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
        """
        create one node
        """
        if not ip and public:
            ip = self.find_available_public_ip()
        elif ip is not None:
            entry = self.list_public_ips(ip=ip, available=True)
            if len(entry) == 0:
                print("ip not available")
            return None
        banner("Create Server")
        print("    Name:    ", name)
        print("    IP:      ", ip)
        print("    Image:   ", image)
        print("    Size:    ", size)
        print("    Public:  ", public)
        print("    Key:     ", key)
        print("    location:", location)
        print("    timeout: ", timeout)
        print("    secgroup:", secgroup)
        print("    group:   ", group)

        # Validate if there is any VM with same tag name and state other than Terminated.
        # If there is any VM, throw error

        ec2_reservations = self.info(name)['Reservations']

        if ec2_reservations:
            reservation_instances = None
            for reservation in ec2_reservations:
                reservation_instances = list(
                    filter(lambda instance: instance['State']['Name'] != 'terminated', reservation['Instances']))

            if reservation_instances:
                Console.error("Tag name already exists, Please use different tag name.")
                return

        if secgroup is None:
            secgroup = 'default'
        #
        # BUG: the tags seem incomplete
        #
        new_ec2_instance = self.ec2_resource.create_instances(
            ImageId=image,
            InstanceType=size,
            MaxCount=1,
            MinCount=1,
            SecurityGroups=[secgroup],
            TagSpecifications=[{'ResourceType': 'instance',
                                'Tags': [
                                    {
                                        'Key': 'cm.name',
                                        'Value': name
                                    }, ]}]
        )
        new_ec2_instance = new_ec2_instance[0]
        waiter = self.ec2_client.get_waiter('instance_exists')

        waiter.wait(Filters=[{'Name': 'instance-id',
                              'Values': [new_ec2_instance.instance_id]}],
                    WaiterConfig={
                        'Delay': 20,
                        'MaxAttempts': timeout / 20
                    }
                    )
        print("Instance created...")
        # if IP provided, Attach it to new instance
        if ip:
            self.attach_public_ip(name, ip)
        if metadata is None:
            metadata = {}
        metadata['cm.image'] = image
        metadata['cm.flavor'] = size
        metadata['cm.user'] = self.user
        metadata['cm.kind'] = "vm"
        self.set_server_metadata(name, metadata)
        data = self.info(name=name)
        data['name'] = name
        data['kind'] = 'aws',
        data['status'] = new_ec2_instance.state['Name'],
        data['created'] = new_ec2_instance.launch_time.strftime("%m/%d/%Y, %H:%M:%S") if new_ec2_instance.launch_time else '',
        data['updated'] = new_ec2_instance.launch_time.strftime("%m/%d/%Y, %H:%M:%S") if new_ec2_instance.launch_time else '',
        data['name'] = new_ec2_instance.tags[0]['Value'] if new_ec2_instance.tags else '',
        data['instance_id'] = new_ec2_instance.id,
        data['image'] = new_ec2_instance.image_id,
        data['public_ips'] = new_ec2_instance.public_ip_address,
        data['private_ips'] = new_ec2_instance.private_ip_address

        output = self.update_dict(data, kind="vm")[0]
        return output

    def rename(self, name=None, destination=None):
        # TODO: Sriman
        """
        rename a node

        :param destination:
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
        # TODO: Vafa
        """
        Lists the keys on the cloud

        :return: dict
        """
        return self.ec2_client.describe_key_pairs()

    def key_upload(self, key=None):
        # TODO: Vafa
        # The gey is stored in the database, we do not create a new keypair,
        # we upload our local key to aws
        # BUG name=None, wrong?
        # ~/.ssh/id_rsa.pub

        """
        uploads the key specified in the yaml configuration to the cloud
        :param key:
        :return:
        """
        return self.ec2_client.create_key_pair(KeyName=key)

    def key_delete(self, name=None):
        # TODO: Vafa
        """
        deletes the key with the given name
        :param name: The name of the key
        :return:
        """
        return self.ec2_client.delete_key_pair(KeyName=name)

    def delete_server_metadata(self, name):
        """
        gets the metadata for the server

        :param name: name of the fm
        :return:
        """
        raise NotImplementedError

    def images(self, **kwargs):
        # TODO: Vafa
        """
        Lists the images on the cloud
        :return: dict
        """
        raise NotImplementedError

    def image(self, name=None):
        # TODO: Vafa
        """
        Gets the image with a given nmae
        :param name: The name of the image
        :return: the dict of the image
        """
        raise NotImplementedError

    def flavors(self, **kwargs):
        # TODO: Alex
        """
        Lists the flavors on the cloud

        :return: dict of flavors
        """
        raise NotImplementedError

    def flavor(self, name=None):
        # TODO: Alex
        """
        Gets the flavor with a given name
        :param name: The name of the flavor
        :return: The dict of the flavor
        """
        raise NotImplementedError

    def update_dict(self, elements, kind=None):
        #
        # please compare to openstack, i made some changes there
        # THIS IS THE FUNCTION THAT INTEGRATES WITH CLOUDMESH
        # THIS IS A KEY POINT WITHOUT THI S THE COMMANDS WILL NOT WORK
        # EACH dict that you return in a method must apply this update on the
        # dicts. it adds the cm dict.
        #
        """
        THis function adds a cloudmesh cm dict to each dict in the list
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
                try:
                    entry['comment'] = entry['public_key'].split(" ", 2)[2]
                except:
                    entry['comment'] = ""
                entry['format'] = \
                    entry['public_key'].split(" ", 1)[0].replace("ssh-", "")

            entry["cm"] = {
                "kind": kind,
                "driver": self.cloudtype,
                "cloud": self.cloud,
                "name": entry['name'],
                "updated": entry['updated'],
                "Image": entry['image'],
                "Public IPs": entry['public_ips'],
                "Private IPs": entry['private_ips']

            }
            if kind == 'vm':
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
    # name=Name()
    # name.incr()
    # provider.create(name.get())
    provider.create(name='sriman123')
    print(provider.list())
