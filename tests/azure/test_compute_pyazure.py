###############################################################
# pytest -v --capture=no tests/test_compute_pyazure.py
# pytest  tests/test_compute_pyazure.py
###############################################################

import pytest
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.common3.Benchmark import Benchmark
from cloudmesh.compute.azure.Provider import Provider
from cloudmesh.management.configuration.config import Config
from cloudmesh.management.configuration.name import Name


#
# cms set debug=True
# cms set verbose=True
# cms set timer=True
# cms set cloud=azure
#

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
        self.p = Provider(name="azure")

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
        test_images = self.p.list_images()
        Benchmark.Stop()

        assert test_images is not None

    def test_create_vm(self):
        HEADING()

        Benchmark.Start()
        test_vm = self.p.create()
        Benchmark.Stop()

        assert test_vm is None

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

    def test_restart(self):
        HEADING()

        Benchmark.Start()
        restart_vm = self.p.restart()
        Benchmark.Stop()

        assert restart_vm is not None

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

    # TODO test_resume
    # TODO test_suspend

    def test_benchmark(self):
        Benchmark.print()
