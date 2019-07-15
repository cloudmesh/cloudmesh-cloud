from datetime import datetime
from pprint import pprint

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


    def __init__(self, name=None, configuration="~/.cloudmesh/.cloudmesh4.yaml"):
        super().__init__(name=name, configuration=configuration)
