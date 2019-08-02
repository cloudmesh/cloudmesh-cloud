###############################################################
# pytest -v --capture=no tests/test_compute_database.py
# pytest -v  tests/test_compute_database.py
# pytest -v --capture=no tests/test_compute_database.py:Test_compute_database.<METHIDNAME>
###############################################################
import subprocess
import time
from pprint import pprint

import pytest
from cloudmesh.common.Printer import Printer
from cloudmesh.common.Shell import Shell
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.common.variables import Variables
from cloudmesh.common3.Benchmark import Benchmark
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.configuration.Config import Config
from cloudmesh.management.configuration.SSHkey import SSHkey
from cloudmesh.management.configuration.name import Name

Benchmark.debug()

user = Config()["cloudmesh.profile.user"]
variables = Variables()
cloud = variables.parameter('cloud')

if cloud != "chameloen":
    raise ValueError("cloud is not chameleon")

provider = Provider(name=cloud)

name_generator = Name(schema=f"{user}-vm", counter=1)


def run(label, command):
    result = Shell.run_timed(label, command, service=cloud)
    print(result)
    return result


#
# leverage cms init ...
#

@pytest.mark.incremental
class Test_Compute_Database:

    def setup(self):
        print()

        self.name = str(self.name_generator)
        self.name_generator.incr()

        self.new_name = str(self.name_generator)

        self.secgroupname = "CM4TestSecGroup"
        self.secgrouprule = {"ip_protocol": "tcp",
                             "from_port": 8080,
                             "to_port": 8088,
                             "ip_range": "129.79.0.0/16"}
        self.testnode = None
        print("\n")

    def test_banner(self):
        banner("START", color="RED")

    def test_list_flavors(self):
        HEADING()
        flavors = provider.flavors()

    def test_list_images(self):
        HEADING()
        images = provider.images()

    def test_list_nodes(self):
        HEADING()
        nodes = provider.list()

    def test_list_keys(self):
        HEADING()
        self.keys = provider.keys()

    # pprint(self.keys)

    # print(Printer.flatwrite(self.keys,
    #                    sort_keys=["name"],
    #                    order=["name", "fingerprint"],
    #                    header=["Name", "Fingerprint"])
    #      )

    def test_key_upload(self):
        HEADING()

        key = SSHkey()
        print(key.__dict__)

        provider.key_upload(key)

        self.test_list_keys()

    def test_add_key_from_cli(self):
        HEADING()

        result = run("db add key", f"cms key add {user} "
                                   f"--source=ssh", service="local")
        Benchmark.Start()
        result = run("db list ", f"cms key list", service="local")
        Benchmark.Stop()
        VERBOSE(result)

        assert user in result

    def test_upload_key_from_cli(self):
        HEADING()

        Benchmark.Start()
        result = Shell.run_timed("cms key upload",
                                 f"cms key upload {user}")
        Benchmark.Stop()
        result = Shell.run_timed("cms list", f"cms key upload {user}")

        "cms key list --cloud=chameleon"
        VERBOSE(result)

    def test_list_variables(self):
        HEADING()
        print(256 * "@")
        pprint(provider.user)
        pprint(provider.cloudtype)
        pprint(provider.spec)

    def test_list_keys(self):
        HEADING()
        Benchmark.Start()
        self.keys = provider.keys()
        Benchmark.Stop()
        # pprint(self.keys)

        print(Printer.flatwrite(self.keys,
                                sort_keys=["name"],
                                order=["name", "fingerprint"],
                                header=["Name", "Fingerprint"])
              )

    def test_list_images(self):
        HEADING()
        images = provider.images()

        print(provider.Print(images, kind="image"))

    def test_list_vm(self):
        HEADING()
        vms = provider.list()
        # pprint (vms)
        print(provider.Print(vms, kind="image"))

    def test_list_secgroups(self):
        HEADING()
        secgroups = provider.list_secgroups()
        for secgroup in secgroups:
            print(secgroup["name"])
            rules = provider.list_secgroup_rules(secgroup["name"])
            print(Printer.write(rules,
                                sort_keys=["ip_protocol", "from_port",
                                           "to_port", "ip_range"],
                                order=["ip_protocol", "from_port", "to_port",
                                       "ip_range"],
                                header=["ip_protocol", "from_port", "to_port",
                                        "ip_range"])
                  )

    def test_secgroups_add(self):
        HEADING()
        Benchmark.Start()
        provider.add_secgroup(self.secgroupname)
        Benchmark.Stop()

        self.test_list_secgroups()

    def test_secgroup_rules_add(self):
        HEADING()
        rules = [self.secgrouprule]
        Benchmark.Start()
        provider.add_rules_to_secgroup(self.secgroupname, rules)
        Benchmark.Stop()

        self.test_list_secgroups()

    def test_secgroup_rules_remove(self):
        HEADING()
        rules = [self.secgrouprule]
        Benchmark.Start()
        provider.remove_rules_from_secgroup(self.secgroupname, rules)
        Benchmark.Stop()

        self.test_list_secgroups()

    def test_secgroups_remove(self):
        HEADING()
        Benchmark.Start()
        provider.remove_secgroup(self.secgroupname)
        Benchmark.Stop()

        self.test_list_secgroups()

    def test_create(self):
        HEADING()
        # BUG NEEDE TO BE READ from COnfig()
        image = "CC-Ubuntu16.04"
        size = "m1.medium"
        Benchmark.Start()
        provider.create(name=self.name,
                        image=image,
                        size=size,
                        # username as the keypair name based on
                        # the key implementation logic
                        ex_keyname=self.user,
                        ex_security_groups=['default'])
        Benchmark.Stop()
        time.sleep(5)
        nodes = provider.list()
        node = provider.find(nodes, name=self.name)
        pprint(node)

        nodes = provider.list(raw=True)
        for node in nodes:
            if node.name == self.name:
                self.testnode = node
                break

        assert node is not None

    def test_publicIP_attach(self):
        HEADING()
        pubip = provider.get_publicIP()
        pprint(pubip)
        nodes = provider.list(raw=True)
        for node in nodes:
            if node.name == self.name:
                self.testnode = node
                break
        if self.testnode:
            print("attaching public IP...")
            Benchmark.Start()
            provider.attach_publicIP(self.testnode, pubip)
            Benchmark.Stop()
            time.sleep(5)
        self.test_list_vm()

    # THIS IS FRO LIBCLOUD AND NEED TO JUST BE UPDATEDE FOR GENERAL PROVIDER
    # THIS IS A BUG
    def test_publicIP_detach(self):
        HEADING()
        print("detaching and removing public IP...")
        time.sleep(5)
        nodes = provider.list(raw=True)
        for node in nodes:
            if node.name == self.name:
                self.testnode = node
                break
        ipaddr = self.testnode.public_ips[0]
        # THIS IS A BUG
        Benchmark.Start()
        pubip = provider.cloudman.ex_get_floating_ip(ipaddr)
        provider.detach_publicIP(self.testnode, pubip)
        Benchmark.Stop()
        time.sleep(5)
        self.test_list_vm()

    # def test_printer(self):
    #    HEADING()
    #    nodes = provider.list()

    #    print(Printer.write(nodes, order=["name", "image", "size"]))

    # def test_01_start(self):
    #    HEADING()
    #    provider.start(name=self.name)

    # def test_12_list_vm(self):
    #    self.test_list_vm()

    def test_info(self):
        HEADING()
        Benchmark.Start()
        provider.info(name=self.name)
        Benchmark.Stop()

    def test_destroy(self):
        HEADING()
        Benchmark.Start()
        provider.destroy(names=self.name)
        Benchmark.Stop()

        nodes = provider.list()
        node = provider.find(nodes, name=self.name)

        pprint(node)
        self.test_list_vm()

        #
        # BUG this seems dependent on cloud we want to use cm.status
        #
        assert node["extra"]["task_state"] == "deleting"

    def test_vm_login(self):
        HEADING()
        self.test_list_vm()
        self.test_create()
        # use the self.testnode for this test
        time.sleep(30)
        self.test_publicIP_attach()
        time.sleep(5)
        nodes = provider.list(raw=True)
        for node in nodes:
            if node.name == self.name:
                self.testnode = node
                break
        # pprint (self.testnode)
        # pprint (self.testnode.public_ips)
        pubip = self.testnode.public_ips[0]

        COMMAND = "cat /etc/*release*"

        Benchmark.Start()
        ssh = subprocess.Popen(
            ["ssh", "%s@%s" % (self.clouduser, pubip), COMMAND],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        result = ssh.stdout.readlines()
        Benchmark.Stop()

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
        Benchmark.Start()
        provider.rename(source=self.name, destination=self.new_name)
        Benchmark.Stop()

    # def test_stop(self):
    #    HEADING()
    #    self.stop(name=self.name)

    # def test_suspend(self):
    #    HEADING()
    #    provider.suspend(name=self.name)

    # def test_resume(self):
    #    HEADING()
    #    provider.resume(name=self.name)
