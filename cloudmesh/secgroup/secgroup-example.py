#
# python cloudmesh/secgroup/secgroup-example.py
#
# Draft
#

#
# NOTE: the name is duplicated in the db, but we do not care as there are
# only a few secgroups. Its easier to program when the name is in the info
# filed and the cm dict.
#

from pprint import pprint
from cloudmesh.secgroup.Secgroup import Secgroup, SecgroupRule
from cloudmesh.common.util import banner
from cloudmesh.common.debug import VERBOSE

secgroups = \
    [
        {
            "cm": {
                "kind": "secgroup",
                "name": "default",
                "cloud": "local",
                "type": "group"
            },
            "name": "default",
            "description": "Default security group",
            "rules": [
                "ssh", "icmp", "ssl"
            ]
        },
        {
            "cm": {
                "kind": "secgroup",
                "name": "flask",
                "cloud": "local",
                "type": "group"
            },
            "Name": "flask",
            "Description": "Couchdb security group",
            "rules": [
                "ssh", "icmp", "ssl", "flask", "webserver"
            ]
        },
    ]

secrules = \
    [
        {
            "cm": {
                "kind": "secgroup",
                "name": "ssh",
                "cloud": "local",
                "type": "rule"
            },
            "name": "ssh",
            "protocol": "tcp",
            "ip_range": "0.0.0.0/0",
            "ports": "22:22",
        },
        {
            "cm": {
                "kind": "secgroup",
                "name": "icmp",
                "cloud": "local",
                "type": "rule"
            },
            "name": "icmp",
            "protocol": "icmp",
            "ip_range": "0.0.0.0/0",
            "ports": "",
        },
        {
            "cm": {
                "kind": "secgroup",
                "name": "flask",
                "cloud": "local",
                "type": "rule"
            },
            "name": "flask",
            "protocol": "tcp",
            "ip_range": "0.0.0.0/0",
            "ports": "5000:5000",
        },
        {
            "cm": {
                "kind": "secgroup",
                "name": "webserver",
                "cloud": "local",
                "type": "rule"
            },
            "name": "webserver",
            "protocol": "tcp",
            "ip_range": "0.0.0.0/0",
            "ports": "80:80",
        },
        {
            "cm": {
                "kind": "secgroup",
                "name": "ssl",
                "cloud": "local",
                "type": "rule"
            },
            "name": "ssl",
            "protocol": "tcp",
            "ip_range": "0.0.0.0/0",
            "ports": "443:443",
        }
    ]

banner("secgroups")
pprint (secgroups)

banner("secrules")
pprint (secrules)

banner("secrule")
rule = secrules[0]
pprint (rule)


banner("secgroup")
pprint (secgroups[0])



rules = SecgroupRule()


data = {}
for attribute in ['name','protocol','ip_range', 'ports']:
    data[attribute] = rule[attribute]

VERBOSE(data)
pprint (data)

banner("upload")
rules.add(data)

