###############################################################
# pytest -v --capture=no tests/test_secgroup_database.py
# pytest -v  tests/test_secgroup_database.py
###############################################################

from pprint import pprint
from cloudmesh.secgroup.Secgroup import Secgroup, SecgroupRule
from cloudmesh.common.util import banner
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING

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

banner("secrule")
rule = secrules[0] # use this for our test
pprint (rule)

banner("secgroup")
group = secgroups[0]
pprint(group)

rules = SecgroupRule()
groups = Secgroup()

def example(source, attributes):
    data = {}
    for attribute in attributes:
        data[attribute] = source[attribute]
    return data

def test_upload_rule():
    HEADING(color="HEADER")

    data = example(rule, ['name', 'protocol', 'ip_range', 'ports'])

    banner("upload")
    rules.add(**data)
    found = rules.list()[0]
    pprint(found)
    assert found['name'] == rule['name']


def test_upload_group():
    HEADING(color="HEADER")

    data = example(group, ['name','description','rules'])

    groups.add(**data)
    found = groups.list()[0]
    pprint(found)
    assert found['name'] == group['name']


def test_clear():
    HEADING(color="HEADER")

    groups.clear()
    rules.clear()

    r = rules.list()
    g = groups.list()

    assert len(r) == 0
    assert len(g) == 0

def populate():
    HEADING(color="HEADER")

    test_upload_group()
    test_upload_rule()

def test_add_group():
    HEADING(color="HEADER")

    data = example(group, ['name', 'description', 'rules'])
    name = group['name']

    groups.add(**data)
    groups.add(name=name, rules="gregor")

    found = groups.list(name=name)[0]
    assert type(found) == dict
    VERBOSE(found, label="add rule gregor")
    assert "gregor" in found["rules"]

def test_delete_group():
    HEADING(color="HEADER")

    data = example(group, ['name', 'description', 'rules'])
    name = group['name']

    groups.delete(name=name, rules="gregor")
    found = groups.list(name=name)[0]
    VERBOSE(found, label=f"delete rule gregor from {name}")

    assert "gregor" not in found["rules"]

def test_remove_rule():
    name = rule['name']
    rules.remove(name=name)
    found = rules.list()

    VERBOSE(found, label=f"remove rule {name}")

    assert len(found) == 0


def test_remove_group():
    name = group['name']
    groups.remove(name=name)
    found = groups.list()

    VERBOSE(found, label=f"remove rule {name}")

    assert len(found) == 0
