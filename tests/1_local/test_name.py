###############################################################
# pytest -v --capture=no tests/1_basic/test_name.py
# pytest -v  tests/1_basic/test_name.py
# pytest -v --capture=no  tests/1_basic/test_name.py:Test_name.<METHIDNAME>
###############################################################
import os
from pprint import pprint

import pytest
from cloudmesh.common.util import path_expand
from cloudmesh.common3.Benchmark import Benchmark
from cloudmesh.management.configuration.name import Name

path = path_expand("~/.cloudmesh/name.yaml")
data = {
    'counter': 1,
    'path': path,
    'kind': "vm",
    'schema': "{experiment}-{group}-{user}-{kind}-{counter}",
    'experiment': 'exp',
    'group': 'group',
    'user': 'user'
}

try:
    os.remove(path)
except:
    pass

n = None


@pytest.mark.incremental
class TestName:

    def test_define(self):
        Benchmark.Start()
        n = Name()
        Benchmark.Start()
        assert dict(data) == n.dict()

    def test_define_new(self):
        os.remove(path)

        Benchmark.Start()
        n = Name(schema="{user}-{kind}-{counter}",
                 counter="3",
                 user="gregor",
                 kind="vm")
        Benchmark.Stop()
        data = n.dict()
        pprint(data)
        assert data == dict({'counter': 3,
                             'kind': 'vm',
                             'path': '/Users/grey/.cloudmesh/name.yaml',
                             'schema': '{user}-{kind}-{counter}',
                             'user': 'gregor'})

    def test_name_reset(self):
        n = Name()
        Benchmark.Start()
        n.reset()
        Benchmark.Stop()
        assert n.counter == 1

    def test_name_print(self):
        n = Name()
        Benchmark.Start()
        print(n)
        Benchmark.Start()
        assert str(n) == "gregor-vm-1"

    def test_name_dict(self):
        n = Name()
        pprint(n.dict())
        Benchmark.Start()
        data = n.dict()
        Benchmark.Stop()
        assert data == dict({'counter': 1,
                             'kind': 'vm',
                             'path': '/Users/grey/.cloudmesh/name.yaml',
                             'schema': '{user}-{kind}-{counter}',
                             'user': 'gregor'})

    def test_name_incr(self):
        n = Name()
        Benchmark.Start()
        n.incr()
        Benchmark.Stop()
        print(n)
        assert str(n) == "gregor-vm-2"

    def test_name_counter(self):
        n = Name()
        Benchmark.Start()
        c = n.counter
        Benchmark.Stop()
        print(n.counter)
        assert n.counter == 2

        m = Name()

        pprint(n.dict())
        pprint(m.dict())
        print(m)
        assert str(n) == str(m)

    def test_benchmark(self):
        Benchmark.print()
