# python cloudmesh/compute/awsboto/test_boto.py

from datetime import datetime
from pprint import pprint

import boto3
import yaml
import os
import traceback
import sys
from pprint import pprint
from botocore.exceptions import ClientError

from cloudmesh.provider import ComputeProviderPlugin
from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.management.configuration.config import Config


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

    def __init__(self):
        config = Config()
        credentials = config['cloudmesh.cloud.awsboto.credentials']
        self.access_id = credentials['EC2_ACCESS_ID']
        self.secret_key = credentials['EC2_SECRET_KEY']
        self.region = credentials['region']
        self.session = None
        self.instance_id = None

    def start(self, name=None):
        """
        start a node

        :param name: the unique node name
        :return:  The dict representing the node
        """
        if name is None:
            print("Please provide instance id...")
            return
        self.instance_id = name
        if self.session is None:
            self.session = boto3.Session(aws_access_key_id=self.access_id,
                                         aws_secret_access_key=self.secret_key,
                                         region_name=self.region)
        if self.session is None:
            print("Invalid credentials...")
            return
        ec2_resource = self.session.resource('ec2')
        ec2_client = ec2_resource.meta.client

        try:
            ec2_client.start_instances(InstanceIds=[self.instance_id])
        except ClientError:
            print("Currently instance cant be started...Please try again")

        waiter = ec2_client.get_waiter('instance_running')

        waiter.wait(InstanceIds=self.instance_id)

        print("Instance started...")

    def stop(self, name=None):
        """
        stops the node with the given name

        :param name:
        :return: The dict representing the node including updated status
        """

        if name is None:
            print("Please provide instance id...")
            return
        instance_id = name
        if self.session is None:
            self.session = boto3.Session(aws_access_key_id=self.access_id,
                                         aws_secret_access_key=self.secret_key,
                                         region_name=self.region)
        if self.session is None:
            print("Invalid credentials...")
            return
        ec2_resource = self.session.resource('ec2')
        ec2_client = ec2_resource.meta.client

        try:
            ec2_client.stop_instances(InstanceIds=[instance_id])
        except ClientError:
            print("Currently instance cant be stopped...Please try again")

        waiter = ec2_client.get_waiter('instance_running')

        waiter.wait(InstanceIds=instance_id)

        print("Instance stopped...")

    def info(self, name=None):
        """
        gets the information of a node with a given name

        :param name:
        :return: The dict representing the node including updated status
        """
        if name is None:
            print("Please provide node name...")
            return
        if self.session is None:
            self.session = boto3.Session(aws_access_key_id=self.access_id,
                                         aws_secret_access_key=self.secret_key,
                                         region_name=self.region)
        if self.session is None:
            print("Invalid credentials...")
            return
        ec2_client = self.session.resource('ec2').meta.client

        instance_info = ec2_client.describe_instances(InstanceIds=[name])

        return instance_info

    def list(self):
        """
        list all nodes id

        :return: an array of dicts representing the nodes
        """
        if self.session is None:
            self.session = boto3.Session(aws_access_key_id=self.access_id,
                                         aws_secret_access_key=self.secret_key,
                                         region_name=self.region)
        if self.session is None:
            print("Invalid credentials...")
            return

        ec2_resource = self.session.resource('ec2')
        instance_ids = []
        for each_instance in ec2_resource.instances.all():
            instance_ids.append(each_instance.id)
        return instance_ids

    def reboot(self, name=None):
        """
        Reboot a list of nodes with the given names

        :param names: A list of node names
        :return:  A list of dict representing the nodes
        """
