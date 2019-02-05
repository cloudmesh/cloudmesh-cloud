from pprint import pprint
from cloudmesh.common.util import HEADING
from cloudmesh.compute.libcloud.Provider import Provider
from cloudmesh.management.configuration.config import Config

# nosetest -v --nopature
# nosetests -v --nocapture tests/test_compute_provider.py

class TestName:

    def setup(self):
        self.name="vm01"
        self.new_name="vm02"
        self.p = Provider(name="chameleon")


    def test_01_start(self):
        HEADING()
        self.p.start(name=self.name)


    def test_02_list(self):
        HEADING()
        self.p.list()


    def test_03_info(self):
        HEADING()
        self.p.info(name=self.name)

    def test_04_rename(self):
        HEADING()

        self.p.rename(name=self.name, destination=self.new_name)

    def test_05_destroy(self):
        HEADING()

        self.p.destroy(name=self.new_name)


    #def test_01_create(self):
    #    HEADING()

    #    self.p.create(name=self.name,
    #                  image=None,
    #                  size=None,
    #                  timeout=360,
    #                  **kwargs)



    #def test_01_stop(self):
    #    HEADING()
    #    self.stop(name=self.name)

    #def test_01_suspend(self):
    #    HEADING()
    #    self.p.suspend(name=self.name)


    #def test_01_resume(self):
    #    HEADING()
    #    self.p.resume(name=self.name)
