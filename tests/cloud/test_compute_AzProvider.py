#################################################################
# pytest -v --pature=no tests/azure
# pytest -v --capture=no tests/azure/test_compute_AzProvider.py
#################################################################

import pytest
from cloudmesh.common.util import HEADING
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.compute.libcloud.Provider import Provider


CLOUD = "azazure"

@pytest.mark.incremental
class Testazure(object):

    def setup(self):
        self.p = Provider(name=CLOUD)
        self.name = "testvm1"
        self.group = "test"
        self.location = "eastus"

    def test_login(self):
        HEADING()
        r = self.p.login()

    def test_create_vm(self):
        HEADING()
        r = self.p.create_vm(resource_group=self.group,
                             name=self.name,
                             image="UbuntuLTS",
                             username="ubuntu")
        assert r["location"] == 'eastus'

    def test_list_vm(self):
        HEADING()
        r = self.p.list_vm(resource_group=self.group)
        assert r[0]["name"] == "testvm1"

    def test_04_ssh_vm(self):
        HEADING()
        self.p.ssh_vm(user="ubuntu",
                      resource_group=self.group,
                      name=self.name,
                      command="uname -a")

    def test_connect_vm(self):
        HEADING()
        r = self.p.connect_vm(resource_group=self.group,
                              name=self.name,
                              user='ubuntu')
        assert r['status'] == 0

    def test_stop_vm(self):
        HEADING()
        r = self.p.stop_vm(resource_group=self.group,
                           name=self.name)
        # time.sleep(100)
        assert r['status'] == 0

    def test_start_vm(self):
        HEADING()
        r = self.p.start_vm(resource_group=self.group,
                            name=self.name)
        # time.sleep(100)
        assert r['status'] == 0

    def test_delete_vm(self):
        HEADING()
        r = self.p.delete_vm(resource_group=self.group,
                             name=self.name)
        assert r['status'] == 0
