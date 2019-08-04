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

    def test_resource_group(self):
        HEADING()
        Benchmark.Start()
        test_resource_group = self.p.get_resource_group()
        VERBOSE('RESOURCE GROUP: ' + str(test_resource_group))
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
        VERBOSE('Virtual Machine Created: ' + str(test_vm))

        assert test_vm is not None

    def test_set_server_metadata(self):
        HEADING()

        tags = 'This is my cloudmesh metadata Tag'

        Benchmark.Start()
        test_set_metadata = self.p.set_server_metadata(name=None,cm=tags)
        Benchmark.Stop()
        VERBOSE('Added Metadata to Virtual Machine Created:' +  str(test_set_metadata))

        assert test_set_metadata is not None

    def test_get_server_metadata(self):
        HEADING()

        Benchmark.Start()
        test_get_metadata = self.p.get_server_metadata(self)
        Benchmark.Stop()
        VERBOSE('Get Metadata from Virtual Machine: ' + str(test_get_metadata))

        assert test_get_metadata is not None

    def test_delete_server_metadata(self):
        HEADING()

        Benchmark.Start()
        test_delete_metadata = self.p.delete_server_metadata(None, 'cm')
        Benchmark.Stop()
        VERBOSE('Metadata from Virtual Machine after deleting: ' + str(test_delete_metadata))

        assert test_delete_metadata is not None

    def test_start(self):
        HEADING()

        Benchmark.Start()
        start_vm = self.p.start()
        Benchmark.Stop()
        VERBOSE('Starting Virtual Machine: ' + str(start_vm))

        assert start_vm is not None

    def test_info(self):
        HEADING()

        Benchmark.Start()
        info_vm = self.p.info(None, None)
        Benchmark.Stop()
        VERBOSE('Get Virtual Machine Info: ' + str(info_vm))

        assert info_vm is not None

    def test_list_vms(self):
        HEADING()

        Benchmark.Start()
        list_vm = self.p.list()
        Benchmark.Stop()
        VERBOSE('List Virtual Machines: ' + str(list_vm))

        assert list_vm is not None

    def test_reboot(self):
        HEADING()

        Benchmark.Start()
        reboot_vm = self.p.reboot()
        Benchmark.Stop()
        VERBOSE('Rebooting Virtual Machine: ' + str(reboot_vm))

        assert reboot_vm is not None

    def test_suspend(self):
        HEADING()

        Benchmark.Start()
        suspend_vm = self.p.suspend()
        Benchmark.Stop()
        VERBOSE('Suspend Virtual Machine: ' + str(suspend_vm))

        assert suspend_vm is not None

    def test_resume(self):
        HEADING()

        Benchmark.Start()
        resume_vm = self.p.resume()
        Benchmark.Stop()
        VERBOSE('Resume Virtual Machine: ' + str(resume_vm))

        assert resume_vm is not None

    def test_stop(self):
        HEADING()

        Benchmark.Start()
        stop_vm = self.p.stop()
        Benchmark.Stop()
        VERBOSE('Stop Virtual Machine: ' + str(stop_vm))

        assert stop_vm is not None

    def test_delete(self):
        HEADING()

        Benchmark.Start()
        destroy_vm = self.p.destroy()
        Benchmark.Stop()
        VERBOSE('Delete Virtual Machine: ' + str(destroy_vm))

        assert destroy_vm is None

    def test_benchmark(self):
        Benchmark.print()
