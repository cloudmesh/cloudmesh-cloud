#################################################################
# nosetest -v --nopature
# nosetests -v --nocapture tests/test_compute_google.py
#################################################################

from pprint import pprint
import time
import subprocess
import sys
from cloudmesh.common.util import HEADING
from cloudmesh.compute.libcloud.Provider import Provider as GCloudProvider
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.Printer import Printer
from cloudmesh.common.FlatDict import FlatDict, flatten
from cloudmesh.management.configuration.SSHkey import SSHkey
from cloudmesh.management.configuration.name import Name
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.common.util import banner
from Crypto.PublicKey import RSA
from pathlib import Path
from cloudmesh.common.util import path_expand


class TestName:

    def setup(self):
        banner("setup", c="-")
        self.user = Config()["cloudmesh"]["profile"]["user"]
        self.key_path = path_expand(Config()["cloudmesh"]["profile"]["publickey"])
        f = open(self.key_path, 'r')
        self.key_val = f.read()
  
        self.clouduser = 'cc'
        self.name_generator = Name(
            experiment="exp",
            group="grp",
            user = "user",
            kind="vm",
            counter=1)
        
        self.name = str(self.name_generator)
        self.name_generator.incr()

        self.new_name = str(self.name_generator)

        self.p = GCloudProvider(name="google")

        self.secgroupname = "CM4TestSecGroup"
        self.secgrouprule = {"ip_protocol": "tcp",
                             "from_port": 8080,
                             "to_port": 8088,
                             "ip_range": "129.79.0.0/16"}
        self.testnode = None

    def test_01_list_keys(self):
        HEADING()
        print("List Key Method is not supported by google")

    def test_02_key_upload(self):
        HEADING()
        print("Upload Key method is not supported by google")

    def test_03_list_images(self):
        HEADING()
        images = self.p.images()
        print(Printer.flatwrite(images,
                                sort_keys=("name"),
                                order=["name", "id", "driver"],
                                header=["Name", "Id", "Driver"])
              )

    def test_04_list_flavors(self):
        HEADING()
        flavors = self.p.flavors()
        print(Printer.flatwrite(flavors,
                                sort_keys=("name", "disk"),
                                order=["name", "id", "ram", "disk"],
                                header=["Name", "Id", "RAM", "Disk"])
              )

    def test_04_list_vm(self):
        HEADING()
        vms = self.p.list()
        print(Printer.flatwrite(vms,
                                sort_keys=("name"),
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
    def test_05_list_secgroups(self):
        HEADING()
        print("List security group method is not supported by google")

    def test_06_secgroups_add(self):
        print("List add security groups method is not supported by google")

    def test_07_secgroup_rules_add(self):
        print("List Add security group rules method is not supported by google")

    def test_08_secgroup_rules_remove(self):
        print("Remove security group rules method is not supported by google")

    def test_09_secgroups_remove(self):
        print("Remove security groups method is not supported by google")
 
    def test_10_create(self):
        HEADING()
        image = "ubuntu-minimal-1810-cosmic-v20190402"
        size = "n1-standard-4"
        location = "us-central1-a"
        self.p.create(name=self.name,
                      image=image,
                      size=size,
                      location=location
                      )
        time.sleep(120)
        nodes = self.p.list()
        node = self.p.find(nodes, name=self.name)

        nodes = self.p.list(raw=True)
        for node in nodes:
            if node.name == self.name:
                self.testnode = node
                break

        assert node is not None

    def test_11_publicIP_attach(self):
        HEADING()
        print("Attach Public IP method is not supported by google")

    def test_12_publicIP_detach(self):
        print("Detach Public IP method is not supported by google")

    def test_13_info(self):
        HEADING()
        self.p.info(name=self.name)

    def test_14_stop(self):
        HEADING()
        time.sleep(120)
        self.p.stop(names=self.name)
        #self.test_04_list_vm()

    def test_15_list(self):
        HEADING()
        self.test_04_list_vm()

    def test_16_start(self):
        HEADING()
        time.sleep(120)
        self.p.start(names=self.name)
        self.test_04_list_vm()

    def test_17_list(self):
        HEADING()
        self.test_04_list_vm()

    def test_18_stop(self):
        HEADING()
        self.test_14_stop()
        
    def test_19_destroy(self):
        HEADING()
        time.sleep(120)
        self.p.destroy(names=self.name)
        nodes = self.p.list()
        node = self.p.find(nodes, name=self.name)

        assert node is None

    def test_20_list_vm(self):
        HEADING()
        self.test_04_list_vm()

    def test_21_vm_login(self):
        HEADING()
        self.test_04_list_vm()
        self.test_10_create()
        time.sleep(60)
        nodes = self.p.list(raw=True)
        for node in nodes:
            if node.name == self.name:
                self.testnode = node
                break
        pubip = self.testnode.public_ips[0]

        command = "cat /etc/*release*"

        ssh = subprocess.Popen(
            ["ssh", "%s" % (pubip), "%s" % (command)],
            #["ssh", "%s@%s" % (self.clouduser, pubip), COMMAND],
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
     
    def test_22_stop(self):
        HEADING()
        self.test_14_stop()

    def test_23_list(self):
        HEADING()
        self.test_04_list_vm()

    def test_23_destroy(self):
        HEADING()
        time.sleep(120)
        self.test_19_destroy()

    def test_24_list(self):
        HEADING()
        self.test_04_list_vm()

