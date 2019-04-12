#################################################################
# nosetest -v --nopature
# nosetests -v --nocapture tests/test_azure_cli.py
#################################################################

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
from azprovider import AzureProvider


class Testazure(object):

    def setup(self):
        self.p = AzureProvider()
        self.name = "testvm1"
        self.group = "test"
        self.location = "eastus"

    def test_01_login(self):
        HEADING()
        pprint(self.p.login())

    def test_02_create_vm(self):
        HEADING()
        pprint(self.p.create_vm(resource_group=self.group,
                                name=self.name,
                                image="UbuntuLTS",
                                username="ubuntu"))

    def test_03_list_vm(self):
        HEADING()
        pprint(self.p.list_vm(resource_group=self.group))

    def test_04_ssh_vm(self):
        HEADING()
        self.p.ssh_vm(user="ubuntu",
                      resource_group=self.group,
                      name=self.name,
                      command="uname -a")

    def test_05_connect_vm(self):
        HEADING()
        self.p.connect_vm(resource_group=self.group,
                          name=self.name,
                          user='ubuntu')

    def test_06_stop_vm(self):
        HEADING()
        self.p.stop_vm(resource_group=self.group,
                       name=self.name)
        time.sleep(100)

    def test_07_start_vm(self):
        HEADING()
        self.p.start_vm(resource_group=self.group,
                        name=self.name)
        time.sleep(100)

    def test_08_delete_vm(self):
        HEADING()
        self.p.delete_vm(resource_group=self.group,
                         name=self.name)
