#################################################################
# pytest -v --capture=no tests/google
# pytest -v --capture=no tests/google/test_compute_google.py
#################################################################

import pytest
from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.compute.libcloud.Provider import Provider as GCloudProvider
from cloudmesh.management.configuration.config import Config
from cloudmesh.management.configuration.name import Name


@pytest.mark.incremental
class TestName:

    def setup(self):
        banner("setup", c="-")
        self.user = Config()["cloudmesh"]["profile"]["user"]
        self.key_path = path_expand(
            Config()["cloudmesh"]["profile"]["publickey"])
        f = open(self.key_path, 'r')
        self.key_val = f.read()

        self.clouduser = 'cc'
        self.name_generator = Name(
            schema=f"{self.user}-vm",
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

    def test_list_keys(self):
        HEADING()
        print("List Key Method is not supported by google")

    def test_key_upload(self):
        HEADING()
        print("Upload Key method is not supported by google")

    def test_list_images(self):
        HEADING()
        images = self.p.images()
        print(Printer.flatwrite(images,
                                sort_keys=("name"),
                                order=["name", "id", "driver"],
                                header=["Name", "Id", "Driver"])
              )

    def test_list_flavors(self):
        HEADING()
        flavors = self.p.flavors()
        print(Printer.flatwrite(flavors,
                                sort_keys=("name", "disk"),
                                order=["name", "id", "ram", "disk"],
                                header=["Name", "Id", "RAM", "Disk"])
              )

    def test_list_vm(self):
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

    def test_list_secgroups(self):
        HEADING()
        print("List security group method is not supported by google")

    def test_secgroups_add(self):
        print("List add security groups method is not supported by google")

    def test_secgroup_rules_add(self):
        print("List Add security group rules method is not supported by google")

    def test_secgroup_rules_remove(self):
        print("Remove security group rules method is not supported by google")

    def test_secgroups_remove(self):
        print("Remove security groups method is not supported by google")

    def test_create(self):
        HEADING()
        image = "ubuntu-minimal-1810-cosmic-v20190402"
        size = "n1-standard-4"
        location = "us-central1-a"
        self.p.create(name=self.name,
                      image=image,
                      size=size,
                      location=location
                      )
        nodes = self.p.list()
        node = self.p.find(nodes, name=self.name)

        nodes = self.p.list(raw=True)
        for node in nodes:
            if node.name == self.name:
                self.testnode = node
                break

        assert node is not None

    def test_publicIP_attach(self):
        HEADING()
        print("Attach Public IP method is not supported by google")

    def test_publicIP_detach(self):
        print("Detach Public IP method is not supported by google")

    def test_info(self):
        HEADING()
        self.p.info(name=self.name)

    def test_stop(self):
        HEADING()
        try:
            self.p.stop(names=self.name)
            self.test_list_vm()
        except:
            self.test_list_vm()

    def test_list(self):
        HEADING()
        self.test_list_vm()

    def test_start(self):
        HEADING()
        self.p.start(names=self.name)
        self.test_list_vm()

    def test_destroy(self):
        HEADING()
        try:
            self.p.stop(names=self.name)
            self.test_list_vm()
        except:
            self.test_list_vm()
        self.p.destroy(names=self.name)
        nodes = self.p.list()
        node = self.p.find(nodes, name=self.name)

        assert node is None

    def test_vm_login(self):
        HEADING()
        self.test_list_vm()
        self.test_create()
        self.p.ssh(name=self.name, command="cat /etc/*release*")
        try:
            self.p.stop(names=self.name)
            self.test_list_vm()
        except:
            self.test_list_vm()

        self.p.destroy(names=self.name)
