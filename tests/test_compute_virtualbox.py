#################################################################
# nosetest -v --nopature
# nosetests -v --nocapture tests/test_compute_virtualbox.py
#################################################################

from pprint import pprint
import time
import subprocess
import sys
from cloudmesh.common.util import HEADING
from cloudmesh.compute.virtualbox.Provider import Provider
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.Printer import Printer
from cloudmesh.common.FlatDict import FlatDict, flatten
from cloudmesh.management.configuration.SSHkey import SSHkey
from cloudmesh.management.configuration.name import Name
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.common.util import banner
from pathlib import Path
from cloudmesh.common.util import path_expand

class TestName:

    image_test = False
    vbox_version = '6.0.4'
    image_name = "generic/ubuntu1810"
    size=1024

    def print_images(self):
        images = self.p.images()
        print(Printer.flatwrite(
            images,
            sort_keys=("name"),
            order=["name", "provider", "version"],
            header=["Name", "Provider", "Version"]))

    def next_name(self):
        self.name_generator.incr()
        self.new_name = str(self.name_generator)
        return self.new_name

    def setup(self):
        banner("setup", c="-")
        self.user = Config()["cloudmesh.profile.user"]
        self.name_generator = Name(
            experiment="exp",
            group="grp",
            user=self.user,
            kind="vm",
            counter=1)

        self.name = str(self.name_generator)
        self.name_generator.incr()
        self.new_name = str(self.name_generator)
        self.p = Provider(name="vbox")


    def test_01_version(self):
        HEADING()
        r = self.p.version()
        pprint(r)
        assert self.vbox_version == r["virtualbox"]["extension"]["version"]
        assert self.vbox_version == r["virtualbox"]["version"]


    def test_02_list_os(self):
        HEADING()
        ostypes = self.p.list_os()
        print(Printer.write(
            ostypes,
            order=["id", "64_bit", "description", "family_descr", "family_id"],
            header=["id", "64_bit", "description", "family_descr", "family_id"]))


    def test_03_name(self):
        HEADING()
        print (self.name)
        assert self.name  == "exp-grp-{user}-vm-1".format(user=self.user)

    def test_04_list_images(self):
        HEADING()
        self.print_images()

    def test_05_delete_image(self):
        HEADING()
        if self.image_test:
            name = "generic/ubuntu1810"
            try:
                images = self.p.delete_image(self.image_name)
                print ("delete", self.image_name)
            except:
                print ("image", self.image_name, "nor found")
            self.print_images()
        else:
            print("not executed as image_test is not True. ok")

    def test_06_add_image(self):
        HEADING()
        if self.image_test:
            images = self.p.add_image(self.image_name)
            print("I", images)
            self.print_images()
            assert images.status == 0
        else:
            print("not executed as image_test is not True. ok")

    def test_07_list_vm(self):
        HEADING()

        vms = self.p.info()
        pprint (vms)
        print(Printer.flatwrite(vms,
                                order=["vagrant.name",
                                       "vbox.name",
                                       "vagrant.id",
                                       "vagrant.provider",
                                       "vagrant.state",
                                       "vagrant.hostname"],
                                header=["name",
                                        "vbox",
                                        "id",
                                        "provider",
                                        "state",
                                        "hostname"]))



    def test_10_create(self):
        HEADING()

        name = self.next_name()

        print ("Name", name)

        self.p.create(name=self.name,
                      image=self.image_name,
                      size=self.size,
                      # username as the keypair name based on
                      # the key implementation logic
                      ex_keyname=self.user,
                      ex_security_groups=['default'])


        directory = Path(path_expand("~/.cloudmesh/vagrant/exp-grp-gregor-vm-1"))

        assert directory.is_dir()


        time.sleep(5)
        nodes = self.p.list()
        pprint(nodes)

        node = self.p.find(nodes, name=self.name)
        pprint(node)

        nodes = self.p.list(raw=False)
        for node in nodes:
            if node.name == self.name:
                self.testnode = node
                break

        assert node is not None

class other:

    def test_04_list_flavors(self):
        HEADING()
        flavors = self.p.flavors()
        # pprint (flavors)

        print(Printer.flatwrite(flavors,
                                sort_keys=("name", "vcpus", "disk"),
                                order=["name", "vcpus", "ram", "disk"],
                                header=["Name", "VCPUS", "RAM", "Disk"])
              )

    def test_05_list_secgroups(self):
        HEADING()
        secgroups = self.p.list_secgroups()
        for secgroup in secgroups:
            print(secgroup["name"])
            rules = self.p.list_secgroup_rules(secgroup["name"])
            print(Printer.write(rules,
                                sort_keys=(
                                "ip_protocol", "from_port", "to_port",
                                "ip_range"),
                                order=["ip_protocol", "from_port", "to_port",
                                       "ip_range"],
                                header=["ip_protocol", "from_port", "to_port",
                                        "ip_range"])
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


    def test_11_publicIP_attach(self):
        HEADING()
        pubip = self.p.get_publicIP()
        pprint(pubip)
        nodes = self.p.list(raw=True)
        for node in nodes:
            if node.name == self.name:
                self.testnode = node
                break
        if self.testnode:
            print("attaching public IP...")
            self.p.attach_publicIP(self.testnode, pubip)
            time.sleep(5)
        self.test_04_list_vm()

    def test_12_publicIP_detach(self):
        print("detaching and removing public IP...")
        time.sleep(5)
        nodes = self.p.list(raw=True)
        for node in nodes:
            if node.name == self.name:
                self.testnode = node
                break
        ipaddr = self.testnode.public_ips[0]
        pubip = self.p.cloudman.ex_get_floating_ip(ipaddr)
        self.p.detach_publicIP(self.testnode, pubip)
        time.sleep(5)
        self.test_04_list_vm()

    # def test_11_printer(self):
    #    HEADING()
    #    nodes = self.p.list()

    #    print(Printer.write(nodes, order=["name", "image", "size"]))

    # def test_01_start(self):
    #    HEADING()
    #    self.p.start(name=self.name)

    # def test_12_list_vm(self):
    #    self.test_04_list_vm()


    def test_14_destroy(self):
        HEADING()
        self.p.destroy(names=self.name)
        nodes = self.p.list()
        node = self.p.find(nodes, name=self.name)

        pprint(node)

        assert node["extra"]["task_state"] == "deleting"

    def test_15_list_vm(self):
        self.test_04_list_vm()

    def test_16_vm_login(self):
        self.test_04_list_vm()
        self.test_10_create()
        # use the self.testnode for this test
        time.sleep(30)
        self.test_11_publicIP_attach()
        time.sleep(5)
        nodes = self.p.list(raw=True)
        for node in nodes:
            if node.name == self.name:
                self.testnode = node
                break
        # pprint (self.testnode)
        # pprint (self.testnode.public_ips)
        pubip = self.testnode.public_ips[0]

        COMMAND = "cat /etc/*release*"

        ssh = subprocess.Popen(
            ["ssh", "%s@%s" % (self.clouduser, pubip), COMMAND],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        result = ssh.stdout.readlines()
        if result == []:
            error = ssh.stderr.readlines()
            print("ERROR: %s" % error)
        else:
            print("RESULT:")
            for line in result:
                line = line.decode("utf-8")
                print(line.strip("\n"))

        self.test_14_destroy()
        self.test_04_list_vm()




class other:

    def test_07_rename(self):
        HEADING()

        source = 'b'
        dest = 'c'

        self.p.rename(name=source, destination=dest)
        vms = self.p.list()
        pprint (vms)


    # def test_01_stop(self):
    #    HEADING()
    #    self.stop(name=self.name)

    # def test_01_suspend(self):
    #    HEADING()
    #    self.p.suspend(name=self.name)

    # def test_01_resume(self):
    #    HEADING()
    #    self.p.resume(name=self.name)
