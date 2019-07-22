import datetime
from pprint import pprint

import boto3
from botocore.exceptions import ClientError
from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.management.configuration.config import Config
from cloudmesh.provider import ComputeProviderPlugin


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

    def set_server_metadata(self, name, m):
        raise NotImplementedError

    def get_server_metadata(self, name):
        raise NotImplementedError

    # these are available to be associated
    def list_public_ips(self,
                        ip=None,
                        available=False):
        raise NotImplementedError

    # release the ip
    def delete_public_ip(self, ip=None):
        raise NotImplementedError

    def create_public_ip(self):
        raise NotImplementedError

    def find_available_public_ip(self):
        raise NotImplementedError

    def attach_public_ip(self, node, ip):
        raise NotImplementedError

    def detach_public_ip(self, node, ip):
        raise NotImplementedError

    # see the openstack example it will be almost the same as in openstack
    # other than getting
    # the ip and username
    def ssh(self, vm=None, command=None):
        raise NotImplementedError

    def __init__(self, name=None, configuration="~/.cloudmesh/cloudmesh4.yaml"):
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

        # self.filter_info(**instance_info)

    def list(self):
        """
        list all nodes id

        :return: an array of dicts representing the nodes
        'instance_tag': each_instance.tags[0]['Name']
        """
        instance_ids = []
        for each_instance in self.ec2_resource.instances.all():
            instance_ids.append({'instance_id': each_instance.id,
                                 'instance_tag': each_instance.tags[0]['Value']
                                 })
        return instance_ids
        # return self.update_dict(instance_ids, kind="vm")

    def suspend(self, name=None):
        """
        suspends the node with the given name

        :param name: the name of the node
        :return: The dict representing the node
        """
        raise NotImplementedError

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
            print("Rebooting Instance..Please wait...")
            print(
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
               timeout=360,
               key_name=None,
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
        """
        create one node
        """
        '''
        TO DO: CHECK IF THE TAG NAME EXISTS THEN ASK FOR DIFFERENT TAG NAME
        '''

        tags = [{'ResourceType': 'instance',
                 'Tags': [
                     {
                         'Key': 'Name',
                         'Value': name
                     },
                 ]
                 },
                ]

        if kwargs.get('keyname') is None:
            new_ec2_instance = self.ec2_resource.create_instances(
                ImageId=self.default["image"],
                InstanceType=self.default["size"],
                MaxCount=1,
                MinCount=1,
                TagSpecifications=tags

            )
        else:
            new_ec2_instance = self.ec2_resource.create_instances(
                ImageId=self.default["image"],
                InstanceType=self.default["size"],
                MaxCount=1,
                MinCount=1,
                KeyName=kwargs.get('keyname'),
                TagSpecifications=tags
            )

        waiter = self.ec2_client.get_waiter('instance_exists')

        waiter.wait(Filters=[{'Name': 'instance-id',
                              'Values': [new_ec2_instance[0].instance_id]}],
                    WaiterConfig={
                        'Delay': 20,
                        'MaxAttempts': timeout / 20
                    }
                    )
        print("Instance created...")
        return new_ec2_instance

    def rename(self, name=None, destination=None):
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
        """
        Lists the keys on the cloud

        :return: dict
        """
        return self.ec2_client.describe_key_pairs()

    def key_upload(self, key=None):
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
        """
        deletes the key with the given name
        :param name: The name of the key
        :return:
        """
        return self.ec2_client.delete_key_pair(KeyName=name)

    def images(self, **kwargs):
        """
        Lists the images on the cloud
        :return: dict
        """
        raise NotImplementedError

    def image(self, name=None):
        """
        Gets the image with a given nmae
        :param name: The name of the image
        :return: the dict of the image
        """
        raise NotImplementedError

    def flavors(self, **kwargs):
        """
        Lists the flavors on the cloud

        :return: dict of flavors
        """
        raise NotImplementedError

    def flavor(self, name=None):
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
                "name": entry['name']
            }
            if kind == 'vm':
                entry["cm"]["updated"] = str(datetime.utcnow())
                if "created_at" in entry:
                    entry["cm"]["created"] = str(entry["created_at"])
                    # del entry["created_at"]
                else:
                    entry["cm"]["created"] = entry["modified"]
            elif kind == 'flavor':
                entry["cm"]["created"] = entry["updated"] = str(
                    datetime.utcnow())

            elif kind == 'image':
                entry['cm']['created'] = str(datetime.utcnow())
                entry['cm']['updated'] = str(datetime.utcnow())
            # elif kind == 'secgroup':
            #    pass

            d.append(entry)
        return d

    def get_list(self, d, kind=None, debug=False, **kwargs):
        """
        Lists the dict d on the cloud
        :return: dict or libcloud object
        """

        if self.cloudman:
            entries = []
            for entry in d:
                entries.append(dict(entry))
            if debug:
                pprint(entries)

            return self.update_dict(entries, kind=kind)
        return None


if __name__ == "__main__":
    provider = Provider(name='awsboto')
