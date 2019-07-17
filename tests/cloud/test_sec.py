from pprint import pprint

import pytest
from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import HEADING
from cloudmesh.management.configuration.name import Name
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.management.configuration.config import Config
from cloudmesh.common3.Shell import Shell
from cloudmesh.common.Shell import Shell
from cloudmesh.secgroup.Secgroup import Secgroup
from cloudmesh.secgroup.Secgroup import SecgroupExamples
from cloudmesh.secgroup.Secgroup import SecgroupRule
from cloudmesh.common.StopWatch import StopWatch

rules = SecgroupRule()
groups = Secgroup()


def run(label, command):
    #result = Shell.run_timed(label, command, service="local")
    result = Shell.execute(command)
    print(result)
    return result




run("clear", "cms sec clear")

r = rules.list()
g = groups.list()

assert len(r) == 0
assert len(g) == 0

run("load", "cms sec load")

r = rules.list()
g = groups.list()

assert len(r) > 0
assert len(g) > 0

examples = SecgroupExamples()
assert len(g) == len(examples.secgroups)
assert len(r) == len(examples.secrules)


result = run("clear", "cms sec list")

print ("OOO", result)
r = rules.list()
g = groups.list()
print ("ZZZ", len(r))
for entry in r:
    print ("YYY", entry['name'])
    assert entry['name'] in result
for entry in g:
    assert entry['name'] in result


StopWatch.benchmark()

