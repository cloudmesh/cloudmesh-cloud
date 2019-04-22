###############################################################
# pytest -v --capture=no tests/test_name.py
# pytest -v  tests/test_name.py
# pytest -v --capture=no  tests/test_name.py:Test_name.<METHIDNAME>
###############################################################
from pprint import pprint
from cloudmesh.common.util import HEADING
from cloudmesh.management.configuration.name import Name
import pytest


# nosetest -v --nopature
# nosetests  tests/test_name.py

@pytest.mark.incremental
class TestName:

    def setup(self):
        pass

    def test_Name(self):
        HEADING()

        n = Name(experiment="exp",
                 group="grp",
                 user="gregor",
                 kind="vm",
                 counter=1)

        n.reset()
        assert n.counter == 1

        print(n)
        assert str(n) == "exp-grp-gregor-vm-1"

        pprint(n.dict())

        print(n.get("container"))
        print(n)
        assert str(n) == "exp-grp-gregor-container-1"

        n.incr()
        print(n)
        assert str(n) == "exp-grp-gregor-container-2"

        print(n.counter)
        assert n.counter == 2

        m = Name()

        pprint(n.dict())
        pprint(m.dict())
        print(m)
        assert str(n) == str(m)
