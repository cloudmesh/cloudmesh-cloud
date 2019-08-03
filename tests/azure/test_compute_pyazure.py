###############################################################
# pytest -v --capture=no tests/azure/test_compute_pyazure.py
# pytest  tests/azure/test_compute_pyazure.py
###############################################################

CLOUD="azure"

import pytest
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.common3.Benchmark import Benchmark

from cloudmesh.configuration.Config import Config
from cloudmesh.management.configuration.name import Name


if CLOUD == "azure":
    from cloudmesh.compute.azure.Provider import Provider


Benchmark.debug()

@pytest.mark.incremental
class TestAzure:

    def setup(self):
        banner("setup", c="-")
        self.user = Config()["cloudmesh.profile.user"]
        self.name_generator = Name(
            schema=f"{self.user}-vm",
            counter=1)

        self.name = str(self.name_generator)
        self.name_generator.incr()

        self.new_name = str(self.name_generator)
        self.p = Provider(name=CLOUD)

        print()

    def test_resource_group(self):
        HEADING()
        Benchmark.Start()
        test_resource_group = self.p.get_resource_group()
        VERBOSE(" ".join('RESOURCE GROUP ID: ' + test_resource_group.id))
        Benchmark.Stop()

        assert test_resource_group is not None

    def test_list_images(self):
        HEADING()

        Benchmark.Start()
        test_images = self.p.images()
        Benchmark.Stop()

        assert test_images is not None

    def test_list_flavors(self):
        HEADING()

        Benchmark.Start()
        test_flavors = self.p.flavors()
        Benchmark.Stop()

        assert test_flavors is not None

    def test_create_vm(self):
        HEADING()

        Benchmark.Start()
        test_vm = self.p.create()
        Benchmark.Stop()

        assert test_vm is not None

    def test_set_server_metadata(self):
        HEADING()

        Benchmark.Start()
        test_set_metadata = self.p.set_server_metadata(self,m=None)
        Benchmark.Stop()

        assert test_set_metadata is not None

    def test_get_server_metadata(self):
        HEADING()

        Benchmark.Start()
        test_get_metadata = self.p.get_server_metadata(self)
        Benchmark.Stop()

        assert test_get_metadata is not None

    def test_delete_server_metadata(self):
        HEADING()

        Benchmark.Start()
        test_delete_metadata = self.p.delete_server_metadata(None, 'tag 1')
        Benchmark.Stop()

        assert test_delete_metadata is not None

    def test_start(self):
        HEADING()

        Benchmark.Start()
        start_vm = self.p.start()
        Benchmark.Stop()

        assert start_vm is not None

    def test_info(self):
        HEADING()

        Benchmark.Start()
        info_vm = self.p.info(None, None)
        Benchmark.Stop()

        print(info_vm)

        assert info_vm is not None

    def test_list_vms(self):
        HEADING()

        Benchmark.Start()
        list_vm = self.p.list()
        Benchmark.Stop()

        assert list_vm is not None

    def test_reboot(self):
        HEADING()

        Benchmark.Start()
        reboot_vm = self.p.reboot()
        Benchmark.Stop()

        assert reboot_vm is not None

    def test_suspend(self):
        HEADING()

        Benchmark.Start()
        suspend_vm = self.p.suspend()
        Benchmark.Stop()

        assert suspend_vm is not None

    def test_resume(self):
        HEADING()

        Benchmark.Start()
        resume_vm = self.p.resume()
        Benchmark.Stop()

        assert resume_vm is not None

    def test_stop(self):
        HEADING()

        Benchmark.Start()
        stop_vm = self.p.stop()
        Benchmark.Stop()

        assert stop_vm is not None

    def test_delete(self):
        HEADING()

        Benchmark.Start()
        destroy_vm = self.p.destroy()
        Benchmark.Stop()

        assert destroy_vm is None

    def test_benchmark(self):
        Benchmark.print()
