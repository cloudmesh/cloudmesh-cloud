from pprint import pprint
from cloudmesh.common.util import HEADING
from cloudmesh.compute.libcloud.Provider import Provider

# nosetest -v --nopature
# nosetests -v --nocapture tests/test_Provider.py

class TestName:

    def setup(self):
        pass

    def test_01_start(self):
        HEADING()

        self.p = Provider(name="chameleon")

    def test_01_start(self):
        HEADING()

        self.p.start()


    def test_01_stop(self):
        HEADING()
        self.stop(self, name=None):

    def test_01_info(self):
        HEADING()
        self.p=info(self, name=None):


        self.p=suspend(self, name=None):

        self.p=list(self):

        self.p=resume(self, name=None):


        self.p=destroy(self, name=None):


        self.p=create(self, name=None, image=None, size=None, timeout=360, **kwargs):


        self.p=rename(self, name=None, destination=None):
