###############################################################
# pytest -v --capture=no tests/test_name.py
# pytest -v  tests/test_name.py
# pytest -v --capture=no  tests/test_name.py:Test_name.<METHIDNAME>
###############################################################
from pprint import pprint
from cloudmesh.common.util import HEADING
from cloudmesh.management.configuration.name import Name
import pytest
import os
from cloudmesh.common.util import path_expand
# nosetest -v --nopature
# nosetests  tests/test_name.py

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
        n=Name()
        assert dict(data) == n.dict()

    def test_define_new(self):
        os.remove(path)

        n = Name(schema="{user}-{kind}-{counter}",
                 counter="3",
                 user="gregor",
                 kind="vm")
        data = n.dict()
        pprint(data)
        assert data == dict({'counter': 3,
                             'kind': 'vm',
                             'path': '/Users/grey/.cloudmesh/name.yaml',
                             'schema': '{user}-{kind}-{counter}',
                             'user': 'gregor'})


    def test_name_reset(self):
        n = Name()
        n.reset()
        assert n.counter == 1

    def test_name_print_str(self):
        n = Name()
        print(n)
        assert str(n) == "gregor-vm-1"

    def test_name_dict(self):
        n = Name()
        pprint(n.dict())
        data = n.dict()
        assert data == dict({'counter': 1,
                             'kind': 'vm',
                             'path': '/Users/grey/.cloudmesh/name.yaml',
                             'schema': '{user}-{kind}-{counter}',
                             'user': 'gregor'})

    def test_name_incr(self):
        n=Name()
        n.incr()
        print(n)
        assert str(n) == "gregor-vm-2"

    def test_name_counter(self):
        n = Name()
        print(n.counter)
        assert n.counter == 2

        m = Name()

        pprint(n.dict())
        pprint(m.dict())
        print(m)
        assert str(n) == str(m)
