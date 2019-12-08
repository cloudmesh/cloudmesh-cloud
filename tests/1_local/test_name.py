###############################################################
# pytest -v --capture=no tests/1_local/test_name.py
# pytest -v  tests/1_local/test_name.py
# pytest -v --capture=no  tests/1_local/test_name.py:Test_name.<METHIDNAME>
###############################################################
import os
from pprint import pprint

import pytest
from cloudmesh.common.util import path_expand
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.management.configuration.name import Name
from cloudmesh.common.util import HEADING
from cloudmesh.common.console import Console
from cloudmesh.configuration.Config import Config
from cloudmesh.common.debug import VERBOSE
import sys

Benchmark.debug()

config = Config()
username = config["cloudmesh.profile.user"]

if username == 'TBD':
    Console.error("please set cloudmesh.profile.user in ~/.cloudmesh.yaml")
    sys.exit()

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
        HEADING()
        Benchmark.Start()
        n = Name(**data)
        Benchmark.Stop()

        VERBOSE(data)
        VERBOSE(n.dict())
        assert dict(data) == n.dict()

    def test_define_new(self):
        HEADING()
        os.remove(path)

        Benchmark.Start()
        n = Name(schema="{user}-{kind}-{counter}",
                 counter="3",
                 user=username,
                 kind="vm")
        Benchmark.Stop()
        data = n.dict()
        pprint(data)
        assert data == dict({'counter': 3,
                             'kind': 'vm',
                             'path': path_expand("~/.cloudmesh/name.yaml"),
                             'schema': '{user}-{kind}-{counter}',
                             'user': username})

    def test_name_reset(self):
        HEADING()
        n = Name()
        Benchmark.Start()
        n.reset()
        Benchmark.Stop()
        assert n.counter == 1

    def test_name_print(self):
        HEADING()
        n = Name()
        Benchmark.Start()
        print(n)
        Benchmark.Start()
        assert str(n) == f"{username}-vm-1"

    def test_name_dict(self):
        HEADING()
        n = Name()
        pprint(n.dict())
        Benchmark.Start()
        data = n.dict()
        Benchmark.Stop()
        assert data == dict({'counter': 1,
                             'kind': 'vm',
                             'path': path_expand("~/.cloudmesh/name.yaml"),
                             'schema': '{user}-{kind}-{counter}',
                             'user': username})

    def test_name_incr(self):
        HEADING()
        n = Name()
        Benchmark.Start()
        n.incr()
        Benchmark.Stop()
        print(n)
        assert str(n) == f"{username}-vm-2"

    def test_name_counter(self):
        HEADING()
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
        HEADING()
        Benchmark.print(csv=True)
