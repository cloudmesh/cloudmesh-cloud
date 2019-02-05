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

    def test_00_list_images(self):
        HEADING()
        pprint (self.p.images())

    def test_00_list_flavors(self):
        HEADING()
        pprint (self.p.flavors())

    def test_00_list_vm(self):
        HEADING()
        pprint (self.p.list())

    def test_01_create(self):
        HEADING()
        name = "TestFromCM4"
        image = "CC-Ubuntu16.04"
        size = "m1.medium"
        self.p.create(name=name,
                      image=image,
                      size=size)

        nodes = self.p.list()
        foundnode = False
        for node in nodes:
            if node.name == name:
                foundnode = True
        assert foundnode

    #def test_01_start(self):
    #    HEADING()
    #    self.p.start(name=self.name)

    def test_01_list_vm(self):
        HEADING()
        pprint (self.p.list())

    def test_03_info(self):
        HEADING()
        self.p.info(name=self.name)

    def test_04_rename(self):
        HEADING()

        self.p.rename(name=self.name, destination=self.new_name)

    def test_05_destroy(self):
        HEADING()
        name = "TestFromCM4"
        self.p.destroy(name=name)
        nodes = self.p.list()
        notfoundnode = True
        for node in nodes:
            if node.name == name:
                notfoundnode = False
                break
        #assert notfoundnode

        name = "fwangTest2019"
        self.p.destroy(name=name)

    def test_05_list_vm(self):
        HEADING()
        pprint (self.p.list())


    #def test_01_stop(self):
    #    HEADING()
    #    self.stop(name=self.name)

    #def test_01_suspend(self):
    #    HEADING()
    #    self.p.suspend(name=self.name)


    #def test_01_resume(self):
    #    HEADING()
    #    self.p.resume(name=self.name)
