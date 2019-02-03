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

        print (n)

        pprint(n.dict())

        print (n.get("vm"))
        print(n)


        assert True
