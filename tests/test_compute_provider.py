from pprint import pprint
from cloudmesh.common.util import HEADING
from cloudmesh.compute.libcloud.Provider import Provider
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.Printer import Printer
from cloudmesh.common.FlatDict import FlatDict, flatten
from cloudmesh.management.configuration.SSHkey import SSHkey
from cloudmesh.management.configuration.name import Name
# nosetest -v --nopature
# nosetests -v --nocapture tests/test_compute_provider.py

class TestName:

    def setup(self):
        self.user = Config()["cloudmesh"]["profile"]["user"]
        self.name_generator = Name(
             experiment="exp",
             group="grp",
             user=self.user,
             kind="vm",
             counter=1)

        self.name = str(self.name_generator)
        self.name_generator.incr()

        self.new_name = str(self.name_generator)

        self.p = Provider(name="chameleon")

    def test_01_list_keys(self):
        HEADING()
        self.keys = self.p.keys()
        pprint(self.keys)

        print(Printer.flatwrite(self.keys,
                            sort_keys=("name"),
                            order=["name", "fingerprint"],
                            header=["Name", "Fingerprint"])
              )

    def test_02_key_upload(self):
        HEADING()

        key = SSHkey()
        print (key.__dict__)

        self.p.key_upload(key)


    def test_03_list_images(self):
        HEADING()
        images= self.p.images()
        pprint(images)

        print(Printer.flatwrite(images,
                            sort_keys=("name","extra.minDisk"),
                            order=["name", "extra.minDisk", "updated", "driver"],
                            header=["Name", "MinDisk", "Updated", "Driver"])
              )


    def test_04_list_flavors(self):
        HEADING()
        flavors = self.p.flavors()
        pprint (flavors)

        print(Printer.flatwrite(flavors,
                            sort_keys=("name", "vcpus", "disk"),
                            order=["name", "vcpus", "ram", "disk"],
                            header=["Name", "VCPUS", "RAM", "Disk"])
          )


    def test_04_list_vm(self):
        HEADING()
        vms = self.p.list()
        pprint (vms)


        print(Printer.flatwrite(vms,
                                sort_keys=("name"),
                                order=["name", "state", "extra.task_state", "extra.vm_state", "extra.userId", "private_ips", "public_ips"],
                                header=["Name", "State", "Task state", "VM state", "User Id",
                                       "Private ips", "Public ips"])
              )


    def test_06_create(self):
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

    def test_07_printer(self):
        HEADING()
        nodes = self.p.list()


        print(Printer.write(nodes, order=["name", "image", "size"]))



    #def test_01_start(self):
    #    HEADING()
    #    self.p.start(name=self.name)

    def test_08_list_vm(self):
        HEADING()
        vms = self.p.list()
        pprint(vms)

        print(Printer.flatwrite(vms,
                                sort_keys=("name"),
                                order=["name", "key_name", "state", "extra.task_state", "extra.vm_state", "extra.userId",
                                       "private_ips", "public_ips"],
                                header=["Name", "Key", "State", "Task state", "VM state", "User Id",
                                        "Private ips", "Public ips"])
              )


    def test_09_info(self):
        HEADING()
        self.p.info(name=self.name)



class other:

    def test_10_rename(self):
        HEADING()

        self.p.rename(name=self.name, destination=self.new_name)


    def test_11_destroy(self):
        HEADING()
        self.p.destroy(names=self.name)
        nodes = self.p.list()
        node = self.p.find(nodes, name=self.name)

        pprint (node)

        assert node["state"] is not "running"

    def test_12_list_vm(self):
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
