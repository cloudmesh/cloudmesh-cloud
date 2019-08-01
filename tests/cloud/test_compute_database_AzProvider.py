#################################################################
# pytest -v --pature=no test/azure
# pytest -v --capture=no tests/azure/test_compute_database_AzProvider.py
#################################################################

import pytest
from cloudmesh.common.util import HEADING
from cloudmesh.compute.libcloud.Provider import Provider
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.common3.Benchmark import Benchmark

Benchmark.debug()


@pytest.mark.incremental
class Testazure(object):

    def setup(self):
        self.p = Provider(name="az")
        self.vm_name = "testvm2"
        self.group = self.p.credentials["resourcegroup"]
        self.location = self.p.credentials["location"]

    def test_config(self):
        print(self.p.name)
        print(self.p.kind)
        print(self.p.credentials)
        print(self.location)
        print(self.group)
        assert self.p.name == "az"

    def test_login(self):
        HEADING()
        r = self.p.login()

    def test_create_vm(self):
        HEADING()
        r = self.p.create(
            name=self.vm_name,
            image="UbuntuLTS",
            username="ubuntu")
        assert r["location"] == 'eastus'

    def test_list_vm(self):
        HEADING()
        r = self.p.list()
        assert r[0]["name"] == "testvm1"

    def test_ssh_vm(self):
        HEADING()
        self.p.ssh(user="ubuntu",
                   name=self.vm_name,
                   command="uname -a")

    def test_connect_vm(self):
        HEADING()
        r = self.p.connect(
            name=self.vm_name,
            user='ubuntu')
        assert r['status'] == 0

    def test_stop_vm(self):
        HEADING()
        r = self.p.stop(
            name=self.vm_name)
        # time.sleep(100)
        assert r['status'] == 0

    def test_start_vm(self):
        HEADING()
        r = self.p.start(
            name=self.vm_name)
        # time.sleep(100)
        assert r['status'] == 0

    def test_delete_vm(self):
        HEADING()
        r = self.p.delete(
            name=self.vm_name)
        assert r['status'] == 0
