###############################################################
# pytest -v --capture=no tests/test_compute_pyazure.py
# pytest -v --capture=no tests/test_compute.py
# pytest -v --capture=no tests/test_compute_pyazure.py:Test_compute.<METHIDNAME>
###############################################################
import os
from pprint import pprint

from cloudmesh.compute.azure.PyAzure import Provider
from cloudmesh.common.util import HEADING
from cloudmesh.management.configuration.config import Config
from cloudmesh.management.configuration.name import Name
from cloudmesh.common.variables import Variables
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.parameter import Parameter
import pytest
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.util import banner

#
# cms set debug=True
# cms set verbose=True
# cms set timer=True
# cms set cloud=pyazure
#

@pytest.mark.incremental
class Test_compute:

    def setup(self):

        banner("setup", c="-")
        self.user = Config()["cloudmesh"]["profile"]["user"]
        self.name_generator = Name(
            experiment="exp",
            group="grp",
            user=self.user,
            kind="vm",
            counter=1)

        self.name = str(self.name_generator)
        self.name_generator.incr()

        self.new_name = str(self.name_generator)
        self.p = Provider(name="pyazure")

        print()

    def test_resource_group(self):
        HEADING()
        StopWatch.start("Retrieve Resource Group Started")
        test_resource_group = self.p.get_resource_group()
        VERBOSE(" ".join('RESOURCE GROUP ID: ' + test_resource_group.id))
        StopWatch.stop("Retrieve Resource Group Finished")

        assert test_resource_group is not None

    def test_list_images(self):
        HEADING()

        StopWatch.start("List Images Started")
        test_images = self.p.list_images()
        StopWatch.stop("List Images Finished")

        assert test_images is not None

    def test_create_vm(self):
        HEADING()

        StopWatch.start("Create VM Started")
        test_vm = self.p.create()
        StopWatch.stop("Create VM Finished")

        assert test_vm is None

    def test_start(self):
        HEADING()

        StopWatch.start("Start VM Started")
        start_vm = self.p.start()
        StopWatch.stop("Start VM Finished")

        assert start_vm is not None

    def test_info(self):
        HEADING()

        StopWatch.start("List VM info Started")
        list_vm = self.p.info(None, None)
        StopWatch.stop("List VM Info Finished")

        assert list_vm is not None

    def test_restart(self):
        HEADING()

        StopWatch.start("Restart VM Started")
        restart_vm = self.p.restart()
        StopWatch.stop("Restart VM Finished")

        assert restart_vm is not None

    def test_stop(self):
        HEADING()

        StopWatch.start("Stop VM Started")
        stop_vm = self.p.stop()
        StopWatch.stop("Stop VM Finished")

        assert stop_vm is not None

    def test_delete(self):
        HEADING()

        StopWatch.start("Delete VM Started")
        destroy_vm = self.p.destroy()
        StopWatch.stop("Delete VM Finished")

        assert destroy_vm is None

    # TODO test_resume
    # TODO test_suspend
