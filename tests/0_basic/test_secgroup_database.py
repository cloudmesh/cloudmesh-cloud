###############################################################
# pytest -v --capture=no tests/0_basic/test_secgroup_database.py
# pytest -v  tests/0_basic/test_secgroup_database.py
###############################################################

from pprint import pprint
from cloudmesh.secgroup.Secgroup import Secgroup
from cloudmesh.secgroup.Secgroup import SecgroupRule
from cloudmesh.secgroup.Secgroup import SecgroupExamples
from cloudmesh.common.util import banner
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING


examples = SecgroupExamples()
examples.load()

secgroups = examples.secgroups
secrules = examples.secrules


rules = SecgroupRule()
groups = Secgroup()

print()

def test_clear():
    HEADING(color="HEADER")

    groups.clear()
    rules.clear()

    r = rules.list()
    g = groups.list()

    #print("R", r)
    #print("G", r)

    assert len(r) == 0
    assert len(g) == 0

def test_upload_groups():
    HEADING(color="HEADER")

    names = secgroups.keys()

    for name in names:
        print("add group:", name)
        data = examples.group(name)
        groups.add(**data)

    found = groups.list()
    print(len(found))
    assert len(found) == len (names)
    for entry in found:
        assert entry['name'] in names

def test_upload_rules():
    HEADING(color="HEADER")

    names = secrules.keys()

    # pprint(secrules)
    for name in names:
        print ("add rule:", name)
        data = examples.rule(name)
        rules.add(**data)

    found = rules.list()
    print(len(found))
    assert len(found) == len(names)
    for entry in found:
        assert entry['name'] in names


def test_add_rule_to_group():
    HEADING(color="HEADER")

    original = groups.list()
    name = original[0]["name"]

    groups.add(name=name, rules="gregor")

    found = groups.list(name=name)[0]
    assert type(found) == dict
    assert "gregor" in found["rules"]

    found = groups.list()
    assert len(found) == len(original)

def test_delete_rule_from_group():
    HEADING(color="HEADER")

    original = groups.list()
    name = original[0]["name"]

    groups.delete(name=name, rules="gregor")
    found = groups.list(name=name)[0]

    assert "gregor" not in found["rules"]

    found = groups.list()
    assert len(found) == len(original)
    assert len(found) == len(original)

def test_remove_group():

    name = list(examples.secgroups.keys())[0]

    original = groups.list()

    groups.remove(name=name)
    updated = groups.list()

    print (len(original), "->",  len(updated))

    assert len(updated) == len(original) - 1


def test_remove_rule():
    old = rules.list()
    name = old[0]["name"]

    rules.remove(name=name)

    found = rules.list()

    # VERBOSE(found, label=f"remove rule {name}")

    print(len(old), "->", len(found))

    assert len(found) == len(old) - 1

    assert len(found) == len(secrules) - 1


def test_load_defaults():

    examples = SecgroupExamples()
    examples.load()

    found = groups.list()
    assert len(found) == len(examples.secgroups)

    found = rules.list()
    assert len(found) == len(examples.secrules)


