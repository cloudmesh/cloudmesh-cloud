from pprint import pprint
from cloudmesh.common.util import HEADING
from cloudmesh.management.configuration.name import Name

# nosetest -v --nopature
# nosetests -v --nocapture tests/test_name.py

class TestName:

    def setup(self):
        pass

    def test_01_Name(self):
        HEADING()

        n = Name(experiment="exp",
                 group="grp",
                 user="gregor",
                 kind="vm",
                 counter=1)

        n.reset()
        assert n.counter == 1

        print (n)
        assert str(n) == "exp-grp-gregor-vm-1"

        pprint(n.dict())

        print (n.get("container"))
        print(n)
        assert str(n) == "exp-grp-gregor-container-1"

        n.incr()
        print(n)
        assert str(n) == "exp-grp-gregor-container-2"

        print (n.counter)
        assert n.counter == 2


