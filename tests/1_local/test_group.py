###############################################################
# pytest -v --capture=no tests/1_local/test_group.py
# pytest -v  tests/1_local/test_group.py
# pytest -v --capture=no  tests/1_local/test_group.py:Test_group.<METHIDNAME>
###############################################################
import os
from pprint import pprint

import pytest
from cloudmesh.common.util import path_expand
from cloudmesh.common3.Benchmark import Benchmark
from cloudmesh.management.configuration.name import Name
from cloudmesh.group.Group import Group
from cloudmesh.common.parameter import Parameter
from cloudmesh.common3.DictList import DictList
from cloudmesh.common.util import HEADING
from cloudmesh.common.Printer import Printer


g = Group()
services = Parameter.expand('vm-[1-3]')

@pytest.mark.incremental
class TestName:


    def test_list(self):
        HEADING()
        Benchmark.Start()
        r = g.list(name='test')
        Benchmark.Stop()

    def test_add(self):
        HEADING()
        Benchmark.Start()
        r = g.add(name='test', services='vm-[1-3]', category='vm')
        Benchmark.Stop()


        pprint (r)

        r = g.list(name="test")
        pprint (r)

        members = r[0]['members']
        for member in members:
            assert member['name'] in services

        assert len(members) == len(services)

    def test_members(self):
        HEADING()
        members = g.members(name="test")
        pprint(members)

        print (Printer.write(members))

        for member in members:
            assert member['name'] in services

        assert len(members) == len(services)


    def test_benchmark(self):
        Benchmark.print(sysinfo=False)
