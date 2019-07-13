###############################################################
# pytest -v --capture=no tests/test_secgroup_database.py
# pytest -v  tests/test_secgroup_database.py
###############################################################

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
                "default"
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



banner("secrules")
pprint (secrules)

banner("secrule")
rule = secrules[0] # use this for our test
pprint (rule)


rules = SecgroupRule()

data = {}
for attribute in ['name','protocol','ip_range', 'ports']:
    data[attribute] = rule[attribute]

VERBOSE(data)
pprint (data)

banner("upload")
rules.add(**data)

banner("secgroups")
pprint (secgroups)


banner("secgroup")
group = secgroups[0]
pprint(group)


data = {}
for attribute in ['name','description','rules']:
    data[attribute] = group[attribute]
pprint(data)

group = Secgroup()
name=data['name']

def test_add_group():
    group.add(**data)
    group.add(name=name, rules="gregor")

    found = group.list(name=name)[0]
    VERBOSE(found, label="add gregor")
    assert "gregor" in found["rules"]

def test_delete_group():
    group.delete(name=name, rules="gregor")
    found = group.list(name=name)[0]
    VERBOSE(found, label="remove gregor")

    assert "gregor" not in found["rules"]

