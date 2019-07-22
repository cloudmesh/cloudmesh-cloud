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
g = Group()

@pytest.mark.incremental
class TestName:


    def test_list(self):
        Benchmark.Start()
        r = g.list(name='test')
        Benchmark.Stop()

    def test_add(self):
        print()
        Benchmark.Start()
        r = g.add(name='test', services='vm-[1-3]', category='vm')
        Benchmark.Stop()

        services = Parameter.expand('vm-[1-3]')
        pprint (r)

        r = g.list(name="test")
        pprint (r)

        members = r[0]['members']
        for member in members:
            name = list(member.keys())[0]
            assert name in services

        assert len(members) == len(services)


    def test_benchmark(self):
        Benchmark.print(sysinfo=False)
