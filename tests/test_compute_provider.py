from pprint import pprint
from cloudmesh.common.util import HEADING
from cloudmesh.compute.libcloud.Provider import Provider
from cloudmesh.management.configuration.config import Config

# nosetest -v --nopature
# nosetests -v --nocapture tests/test_compute_provider.py

class TestName:

    def setup(self):
        self.name = "vm-test-vm4"

        self.new_name="vm02"
        self.p = Provider(name="chameleon")

    def test_00_list_images(self):
        HEADING()
        pprint (self.p.images())

    def test_01_list_flavors(self):
        HEADING()
        pprint (self.p.flavors())

    def test_02_list_vm(self):
        HEADING()
        vms = self.p.list()
        pprint (vms)


    def test_03_create(self):
        HEADING()
        image = "CC-Ubuntu16.04"
        size = "m1.medium"
        self.p.create(name=self.name,
                      image=image,
                      size=size)

        nodes = self.p.list()

        node = self.p.find(nodes, name=self.name)

        pprint(node)

        assert node is not None

    #def test_01_start(self):
    #    HEADING()
    #    self.p.start(name=self.name)

    def test_04_list_vm(self):
        HEADING()
        pprint (self.p.list())

    def test_05_info(self):
        HEADING()
        self.p.info(name=self.name)

    def test_06_rename(self):
        HEADING()

        self.p.rename(name=self.name, destination=self.new_name)

    def test_07_destroy(self):
        HEADING()
        self.p.destroy(names=self.name)
        nodes = self.p.list()
        node = self.p.find(nodes, name=self.name)

        pprint (node)

        assert node["state"] is not "running"

    def test_08_list_vm(self):
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
