###############################################################
# pytest -v --capture=no tests/1_local/test_group.py
# pytest -v  tests/1_local/test_group.py
# pytest -v --capture=no  tests/1_local/test_group..py::Test_group::<METHODNAME>
###############################################################

from pprint import pprint

import oyaml as yaml
import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Printer import Printer
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import HEADING
from cloudmesh.group.Group import Group

Benchmark.debug()

g = Group()
services = Parameter.expand('vm-[1-3]')

cloud = "local"


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

        pprint(r)

        r = g.list(name="test")
        pprint(r)

        print(yaml.dump(r))

        members = r[0]['members']
        for member in members:
            assert member['name'] in services

        assert len(members) == len(services)

    def test_members(self):
        HEADING()
        members = g.members(name="test")
        pprint(members)

        print(Printer.write(members))

        for member in members:
            assert member['name'] in services

        assert len(members) == len(services)

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag=cloud)
