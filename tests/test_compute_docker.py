###############################################################
# pytest -v --capture=no tests/test_compute_docker.py
# pytest -v  tests/test_compute_docker.py
# pytest -v --capture=no  tests/test_compute_docker.py:Test_compute_docker.<METHIDNAME>
###############################################################
import subprocess
import time
from pathlib import Path
from pprint import pprint

import docker

from cloudmesh.common.Printer import Printer
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.compute.docker.Provider import Provider
from cloudmesh.management.configuration.config import Config
from cloudmesh.management.configuration.name import Name
import pytest


@pytest.mark.incremental
class TestName:
    os = "ubuntu"
    version = "18.04"

    def next_name(self):
        self.name_generator.incr()
        self.new_name = str(self.name_generator)
        return self.new_name

    def setup(self):
        banner("setup", c="-")
        self.config = Config()
        self.user = self.config["cloudmesh.profile.user"]
        self.config = self.config["cloudmesh.cloud.docker"]
        self.name_generator = Name(
            experiment="exp",
            group="grp",
            user=self.user,
            kind="vm",
            counter=1)

        self.name = str(self.name_generator)
        self.name_generator.incr()
        self.new_name = str(self.name_generator)
        self.p = Provider(name="docker")

    def test_config(self):
        HEADING()
        pprint(self.config)

    def test_version(self):
        HEADING()
        version = self.p.version()
        pprint(version)

        assert "18.09.2" == version["docker"]["version"]
        assert 6247962 <= int(version["docker"]["build"])
        assert "18.09.2" == version.docker.version
        assert 6247962 <= int(version.docker.build)

    '''
    def test_terminal(self):
        HEADING()
        t1 = Shell.terminal()
        t2 = Shell.terminal(command="pwd")
    '''

    def test_images(self):
        HEADING
        images = self.p.images()
        pprint(images)
        """
        order = self.p.output['image']['order']  # not pretty
        header = self.p.output['image']['header']  # not pretty

        print(Printer.flatwrite(images,
                                sort_keys=["Os"],
                                order=order,
                                header=header,
                                output="table"))
        """


class d:

    def test_containers(self):
        HEADING()
        client = docker.from_env()

        containers = client.containers.list()
        pprint(containers)
        """
        order = self.p.output['vm']['order']  # not pretty
        header = self.p.output['vm']['header']  # not pretty

        print(Printer.flatwrite(containers,
                                sort_keys=["Os"],
                                order=order,
                                header=header,
                                output="table"))
        """


class ooo:

    def test_images(self):
        HEADING()
        client = docker.from_env()
        r = client.containers.run("cloudmesh/book", "echo hello world")
        pprint(r)


# noinspection PyPep8,PyPep8
class other:
    def test_list_os(self):
        HEADING()
        ostypes = self.p.list_os()
        print(Printer.write(
            ostypes,
            order=["id", "64_bit", "description", "family_descr", "family_id"],
            header=["id", "64_bit", "description", "family_descr",
                    "family_id"]))

    def test_name(self):
        HEADING()
        print(self.name)
        assert self.name == "exp-grp-{user}-vm-1".format(user=self.user)

    def test_list_images(self):
        HEADING()
        self.print_images()

    def test_delete_image(self):
        HEADING()
        if self.image_test:
            name = "generic/ubuntu1810"
            try:
                images = self.p.delete_image(self.image_name)
                print("delete", self.image_name)
            except:
                print("image", self.image_name, "nor found")
            self.print_images()
        else:
            print("not executed as image_test is not True. ok")

    def test_add_image(self):
        HEADING()
        if self.image_test:
            images = self.p.add_image(self.image_name)
            print("I", images)
            self.print_images()
            assert images.status == 0
        else:
            print("not executed as image_test is not True. ok")

    def test_list_vm(self):
        HEADING()

        vms = self.p.info()
        pprint(vms)
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

    def test_create(self):
        HEADING()

        name = self.next_name()

        print("Name", name)

        self.p.create(name=self.name,
                      image=self.image_name,
                      size=self.size,
                      # username as the keypair name based on
                      # the key implementation logic
                      ex_keyname=self.user,
                      ex_security_groups=['default'])

        directory = Path(
            path_expand("~/.cloudmesh/vagrant/exp-grp-gregor-vm-1"))

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

    def test_list_flavors(self):
        HEADING()
        flavors = self.p.flavors()
        # pprint (flavors)

        print(Printer.flatwrite(flavors,
                                sort_keys=["name", "vcpus", "disk"],
                                order=["name", "vcpus", "ram", "disk"],
                                header=["Name", "VCPUS", "RAM", "Disk"])
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
        self.p.add_secgroup(self.secgroupname)
        self.test_list_secgroups()

    def test_secgroup_rules_add(self):
        rules = [self.secgrouprule]
        self.p.add_rules_to_secgroup(self.secgroupname, rules)
        self.test_list_secgroups()

    def test_secgroup_rules_remove(self):
        rules = [self.secgrouprule]
        self.p.remove_rules_from_secgroup(self.secgroupname, rules)
        self.test_list_secgroups()

    def test_secgroups_remove(self):
        self.p.remove_secgroup(self.secgroupname)
        self.test_list_secgroups()

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

    def test_destroy(self):
        HEADING()
        self.p.destroy(names=self.name)
        nodes = self.p.list()
        node = self.p.find(nodes, name=self.name)

        pprint(node)

        assert node["extra"]["task_state"] == "deleting"

    def test_list_vm(self):
        self.test_list_vm()

    def test_vm_login(self):
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

        self.test_destroy()
        self.test_list_vm()


class other:

    def test_rename(self):
        HEADING()

        source = 'b'
        dest = 'c'

        self.p.rename(source=source, destination=dest)
        vms = self.p.list()
        pprint(vms)

    # def test_stop(self):
    #    HEADING()
    #    self.stop(name=self.name)

    # def test_suspend(self):
    #    HEADING()
    #    self.p.suspend(name=self.name)

    # def test_resume(self):
    #    HEADING()
    #    self.p.resume(name=self.name)
