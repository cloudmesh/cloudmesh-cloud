###############################################################
# pytest -v --capture=no tests/test_compute_openstack.py
# pytest -v  tests/test_compute_openstack.py
# pytest -v --capture=no  tests/test_compute_openstack.py:Test_compute_openstack.<METHIDNAME>
###############################################################
import subprocess
import time
from pprint import pprint

from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.compute.libcloud.Provider import Provider
from cloudmesh.management.configuration.SSHkey import SSHkey
from cloudmesh.management.configuration.config import Config
from cloudmesh.management.configuration.name import Name
from cloudmesh.variables import Variables
from cloudmesh.DEBUG import VERBOSE
import pytest


@pytest.mark.incremental
class TestName:

    def setup(self):
        banner("setup", c="-")
        self.user = Config()["cloudmesh"]["profile"]["user"]
        self.clouduser = 'cc'
        self.name_generator = Name(
            experiment="exp",
            group="grp",
            user=self.user,
            kind="vm",
            counter=1)

        self.name = str(self.name_generator)
        self.name_generator.incr()

        self.new_name = str(self.name_generator)

        variables = Variables()
        # this gives the current default cloud
        cloud = variables['cloud']

        # specify the cloud name to make sure this test
        # is done for the openstack cloud
        #
        self.p = Provider(name="chameleon")

        self.secgroupname = "CM4TestSecGroup"
        self.secgrouprule = {"ip_protocol": "tcp",
                             "from_port": 8080,
                             "to_port": 8088,
                             "ip_range": "129.79.0.0/16"}
        self.testnode = None

    def test_list_keys(self):
        HEADING()
        print(256 * "@")
        pprint(self.p.user)
        pprint(self.p.cloudtype)
        pprint(self.p.spec)

    def test_list_keys(self):
        HEADING()
        self.keys = self.p.keys()
        # pprint(self.keys)

        print(Printer.flatwrite(self.keys,
                                sort_keys=["name"],
                                order=["name", "fingerprint"],
                                header=["Name", "Fingerprint"])
              )

    def test_key_upload(self):
        HEADING()

        key = SSHkey()
        print(key.__dict__)

        self.p.key_upload(key)

        self.test_list_keys()

    def test_list_images(self):
        HEADING()
        images = self.p.images()

        VERBOSE(images)

        print(Printer.flatwrite(images,
                                sort_keys=["name", "extra.minDisk"],
                                order=["name", "extra.minDisk", "updated",
                                       "driver"],
                                header=["Name", "MinDisk", "Updated", "Driver"])
              )

    def test_list_flavors(self):
        HEADING()
        flavors = self.p.flavors()
        # pprint (flavors)

        VERBOSE(flavors)

        print(Printer.flatwrite(flavors,
                                sort_keys=["name", "vcpus", "disk"],
                                order=["name", "vcpus", "ram", "disk"],
                                header=["Name", "VCPUS", "RAM", "Disk"])
              )

    def test_list_vm(self):
        HEADING()
        vms = self.p.list()
        # pprint (vms)

        VERBOSE(vms)

        print(Printer.flatwrite(vms,
                                sort_keys=["name"],
                                order=["name",
                                       "state",
                                       "extra.task_state",
                                       "extra.vm_state",
                                       "extra.userId",
                                       "extra.key_name",
                                       "private_ips",
                                       "public_ips"],
                                header=["Name",
                                        "State",
                                        "Task state",
                                        "VM state",
                                        "User Id",
                                        "SSHKey",
                                        "Private ips",
                                        "Public ips"])
              )

    def test_list_secgroups(self):
        HEADING()
        secgroups = self.p.list_secgroups()
        for secgroup in secgroups:
            print(secgroup["name"])
            rules = self.p.list_secgroup_rules(secgroup["name"])
            print(Printer.write(rules,
                                sort_keys=[
                                    "ip_protocol", "from_port", "to_port",
                                    "ip_range"],
                                order=["ip_protocol", "from_port", "to_port",
                                       "ip_range"],
                                header=["ip_protocol", "from_port", "to_port",
                                        "ip_range"])
                  )

    def test_secgroups_add(self):
        HEADING()
        self.p.add_secgroup(self.secgroupname)
        self.test_list_secgroups()

    def test_secgroup_rules_add(self):
        HEADING()
        rules = [self.secgrouprule]
        self.p.add_rules_to_secgroup(self.secgroupname, rules)
        self.test_list_secgroups()

    def test_secgroup_rules_remove(self):
        HEADING()
        rules = [self.secgrouprule]
        self.p.remove_rules_from_secgroup(self.secgroupname, rules)
        self.test_list_secgroups()

    def test_secgroups_remove(self):
        HEADING()
        self.p.remove_secgroup(self.secgroupname)
        self.test_list_secgroups()

    def test_create(self):
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
        time.sleep(5)
        nodes = self.p.list()
        node = self.p.find(nodes, name=self.name)
        pprint(node)

        nodes = self.p.list(raw=True)
        for node in nodes:
            if node.name == self.name:
                self.testnode = node
                break

        assert node is not None

    def test_publicIP_attach(self):
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
        self.test_list_vm()

    def test_publicIP_detach(self):
        HEADING()
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
        self.test_list_vm()

    # def test_printer(self):
    #    HEADING()
    #    nodes = self.p.list()

    #    print(Printer.write(nodes, order=["name", "image", "size"]))

    # def test_start(self):
    #    HEADING()
    #    self.p.start(name=self.name)

    # def test_list_vm(self):
    #    self.test_list_vm()

    def test_info(self):
        HEADING()
        self.p.info(name=self.name)

    def test_destroy(self):
        HEADING()
        self.p.destroy(names=self.name)
        nodes = self.p.list()
        node = self.p.find(nodes, name=self.name)

        pprint(node)
        self.test_list_vm()

        assert node["extra"]["task_state"] == "deleting"

    def test_vm_login(self):
        HEADING()
        self.test_list_vm()
        self.test_create()
        # use the self.testnode for this test
        time.sleep(30)
        self.test_publicIP_attach()
        time.sleep(5)
        nodes = self.p.list(raw=True)
        for node in nodes:
            if node.name == self.name:
                self.testnode = node
                break
        # pprint (self.testnode)
        # pprint (self.testnode.public_ips)
        pubip = self.testnode.public_ips[0]

        command = "cat /etc/*release*"

        ssh = subprocess.Popen(
            ["ssh", "%s@%s" % (self.clouduser, pubip), command],
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
        self.test_list_vm()


class other:

    def test_rename(self):
        HEADING()

        self.p.rename(source=self.name, destination=self.new_name)

    # def test_stop(self):
    #    HEADING()
    #    self.stop(name=self.name)

    # def test_suspend(self):
    #    HEADING()
    #    self.p.suspend(name=self.name)

    # def test_resume(self):
    #    HEADING()
    #    self.p.resume(name=self.name)
