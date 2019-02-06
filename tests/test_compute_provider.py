from pprint import pprint
from cloudmesh.common.util import HEADING
from cloudmesh.compute.libcloud.Provider import Provider
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.Printer import Printer
from cloudmesh.common.FlatDict import FlatDict, flatten
# nosetest -v --nopature
# nosetests -v --nocapture tests/test_compute_provider.py

class TestName:

    def setup(self):
        self.name = "vm-test-vm4"

        self.new_name="vm02"
        self.p = Provider(name="chameleon")

    def test_00_list_images(self):
        HEADING()
        images= self.p.images()
        pprint(images)

        print(Printer.flatwrite(images,
                            sort_keys=("name","extra.minDisk"),
                            order=["name", "extra.minDisk", "updated", "driver"],
                            header=["Name", "MinDisk", "Updated", "Driver"])
              )


    def test_01_list_flavors(self):
        HEADING()
        flavors = self.p.flavors()
        pprint (flavors)

        print(Printer.flatwrite(flavors,
                            sort_keys=("name", "vcpus", "disk"),
                            order=["name", "vcpus", "ram", "disk"],
                            header=["Name", "VCPUS", "RAM", "Disk"])
          )


    def test_02_list_vm(self):
        HEADING()
        vms = self.p.list()
        pprint (vms)


        print(Printer.flatwrite(vms,
                                sort_keys=("name"),
                                order=["name", "state", "extra.task_state", "extra.vm_state", "extra.userId", "private_ips", "public_ips"],
                                header=["Name", "State", "Task state", "VM state", "User Id",
                                       "Private ips", "Public ips"])
              )


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

    def test_04_printer(self):
        HEADING()
        nodes = self.p.list()


        print(Printer.write(nodes, order=["name", "image", "size"]))



    #def test_01_start(self):
    #    HEADING()
    #    self.p.start(name=self.name)

    def test_05_list_vm(self):
        HEADING()
        vms = self.p.list()
        pprint(vms)

        print(Printer.flatwrite(vms,
                                sort_keys=("name"),
                                order=["name", "state", "extra.task_state", "extra.vm_state", "extra.userId",
                                       "private_ips", "public_ips"],
                                header=["Name", "State", "Task state", "VM state", "User Id",
                                        "Private ips", "Public ips"])
              )


    def test_06_info(self):
        HEADING()
        self.p.info(name=self.name)

    def test_07_rename(self):
        HEADING()

        self.p.rename(name=self.name, destination=self.new_name)

    def test_08_destroy(self):
        HEADING()
        self.p.destroy(names=self.name)
        nodes = self.p.list()
        node = self.p.find(nodes, name=self.name)

        pprint (node)

        assert node["state"] is not "running"

    def test_09_list_vm(self):
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
