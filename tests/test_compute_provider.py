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

        self.secgroupname = "CM4TestSecGroup"
        self.secgrouprule = {"ip_protocol": "tcp",
                              "from_port": 8080,
                              "to_port": 8088,
                              "ip_range": "129.79.0.0/16"}

    def test_01_list_keys(self):
        HEADING()
        self.keys = self.p.keys()
        #pprint(self.keys)

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

        self.test_01_list_keys()


    def test_03_list_images(self):
        HEADING()
        images= self.p.images()
        #pprint(images)

        print(Printer.flatwrite(images,
                            sort_keys=("name","extra.minDisk"),
                            order=["name", "extra.minDisk", "updated", "driver"],
                            header=["Name", "MinDisk", "Updated", "Driver"])
              )


    def test_04_list_flavors(self):
        HEADING()
        flavors = self.p.flavors()
        #pprint (flavors)

        print(Printer.flatwrite(flavors,
                            sort_keys=("name", "vcpus", "disk"),
                            order=["name", "vcpus", "ram", "disk"],
                            header=["Name", "VCPUS", "RAM", "Disk"])
          )


    def test_04_list_vm(self):
        HEADING()
        vms = self.p.list()
        #pprint (vms)


        print(Printer.flatwrite(vms,
                                sort_keys=("name"),
                                order=["name", "state", "extra.task_state", "extra.vm_state", "extra.userId", "extra.key_name", "private_ips", "public_ips"],
                                header=["Name", "State", "Task state", "VM state", "User Id", "SSHKey",
                                       "Private ips", "Public ips"])
              )


    def test_05_list_secgroups(self):
        HEADING()
        secgroups = self.p.list_secgroups()
        for secgroup in secgroups:
            print (secgroup["name"])
            rules = self.p.list_secgroup_rules(secgroup["name"])
            print(Printer.write(rules,
                                sort_keys=("ip_protocol", "from_port", "to_port", "ip_range"),
                                order=["ip_protocol", "from_port", "to_port", "ip_range"],
                                header=["ip_protocol", "from_port", "to_port", "ip_range"])
                 )

    def test_06_secgroups_add(self):
        self.p.add_secgroup(self.secgroupname)
        self.test_05_list_secgroups()

    def test_07_secgroup_rules_add(self):
        rules = [self.secgrouprule]
        self.p.add_rules_to_secgroup(self.secgroupname, rules)
        self.test_05_list_secgroups()

    def test_08_secgroup_rules_remove(self):
        rules = [self.secgrouprule]
        self.p.remove_rules_from_secgroup(self.secgroupname, rules)
        self.test_05_list_secgroups()

    def test_09_secgroups_remove(self):
        self.p.remove_secgroup(self.secgroupname)
        self.test_05_list_secgroups()

    def test_10_create(self):
        HEADING()
        image = "CC-Ubuntu16.04"
        size = "m1.medium"
        self.p.create(name=self.name,
                      image=image,
                      size=size,
                      # username as the keypair name based on
                      # the key implementation logic
                      ex_keyname=self.user,
                      ex_security_groups=['default'])

        nodes = self.p.list()

        node = self.p.find(nodes, name=self.name)

        pprint(node)

        assert node is not None

    #def test_11_printer(self):
    #    HEADING()
    #    nodes = self.p.list()


    #    print(Printer.write(nodes, order=["name", "image", "size"]))



    #def test_01_start(self):
    #    HEADING()
    #    self.p.start(name=self.name)

    def test_12_list_vm(self):
        self.test_04_list_vm()


    def test_13_info(self):
        HEADING()
        self.p.info(name=self.name)

    def test_14_destroy(self):
        HEADING()
        self.p.destroy(names=self.name)
        nodes = self.p.list()
        node = self.p.find(nodes, name=self.name)

        pprint (node)

        assert node["state"] is not "running"

    def test_15_list_vm(self):
        self.test_04_list_vm()

class other:

    def test_10_rename(self):
        HEADING()

        self.p.rename(name=self.name, destination=self.new_name)

    #def test_01_stop(self):
    #    HEADING()
    #    self.stop(name=self.name)

    #def test_01_suspend(self):
    #    HEADING()
    #    self.p.suspend(name=self.name)


    #def test_01_resume(self):
    #    HEADING()
    #    self.p.resume(name=self.name)
