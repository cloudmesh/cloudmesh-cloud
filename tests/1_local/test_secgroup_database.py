###############################################################
# pytest -v --capture=no tests/cloud/test_secgroup_database.py
# pytest -v  tests/cloud/test_secgroup_database.py
###############################################################

from cloudmesh.common.util import HEADING
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.secgroup.Secgroup import Secgroup
from cloudmesh.secgroup.Secgroup import SecgroupExamples
from cloudmesh.secgroup.Secgroup import SecgroupRule

Benchmark.debug()

cloud = "local"

examples = SecgroupExamples()
examples.load()

secgroups = examples.secgroups
secrules = examples.secrules

rules = SecgroupRule()
groups = Secgroup()

print()


def test_clear():
    HEADING(color="HEADER")

    Benchmark.Start()
    groups.clear()
    rules.clear()
    Benchmark.Stop()

    r = rules.list()
    g = groups.list()

    # print("R", r)
    # print("G", r)

    assert len(r) == 0
    assert len(g) == 0


def test_upload_groups():
    HEADING(color="HEADER")

    names = secgroups.keys()

    Benchmark.Start()
    for name in names:
        print("add group:", name)
        data = examples.group(name)
        groups.add(**data)
    Benchmark.Stop()

    found = groups.list()
    print(len(found))
    assert len(found) == len(names)
    for entry in found:
        assert entry['name'] in names


def test_upload_rules():
    HEADING(color="HEADER")

    names = secrules.keys()

    # pprint(secrules)
    Benchmark.Start()
    for name in names:
        print("add rule:", name)
        data = examples.rule(name)
        rules.add(**data)
    Benchmark.Stop()

    found = rules.list()
    print(len(found))
    assert len(found) == len(names)
    for entry in found:
        assert entry['name'] in names


def test_add_rule_to_group():
    HEADING(color="HEADER")

    original = groups.list()
    name = original[0]["name"]

    Benchmark.Start()
    groups.add(name=name, rules="gregor")
    Benchmark.Stop()

    found = groups.list(name=name)[0]
    assert type(found) == dict
    assert "gregor" in found["rules"]

    found = groups.list()
    assert len(found) == len(original)


def test_delete_rule_from_group():
    HEADING(color="HEADER")

    original = groups.list()
    name = original[0]["name"]

    Benchmark.Start()
    groups.delete(name=name, rules="gregor")
    Benchmark.Stop()

    found = groups.list(name=name)[0]

    assert "gregor" not in found["rules"]

    found = groups.list()
    assert len(found) == len(original)
    assert len(found) == len(original)


def test_remove_group():
    HEADING()
    name = list(examples.secgroups.keys())[0]

    original = groups.list()

    Benchmark.Start()
    groups.remove(name=name)
    Benchmark.Stop()

    updated = groups.list()

    print(len(original), "->", len(updated))

    assert len(updated) == len(original) - 1


def test_remove_rule():
    HEADING()
    old = rules.list()
    name = old[0]["name"]

    Benchmark.Start()
    rules.remove(name=name)
    Benchmark.Stop()

    found = rules.list()

    # VERBOSE(found, label=f"remove rule {name}")

    print(len(old), "->", len(found))

    assert len(found) == len(old) - 1

    assert len(found) == len(secrules) - 1


def test_load_defaults():
    HEADING()
    examples = SecgroupExamples()
    examples.load()

    Benchmark.Start()
    found = groups.list()
    Benchmark.Stop()

    assert len(found) == len(examples.secgroups)

    found = rules.list()
    assert len(found) == len(examples.secrules)


def test_benchmark():
    HEADING()
    Benchmark.print(csv=True, sysinfo=False, tag=cloud)
