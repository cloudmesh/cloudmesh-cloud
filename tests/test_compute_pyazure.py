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

    def test_create_nic(self):
        HEADING()

        StopWatch.start("Create Nic Started")
        test_nic = self.p.create_nic()
        VERBOSE(" ".join('NIC ID: '+ test_nic.id))
        StopWatch.stop("Create Nic Finished")

        assert test_nic is not None

    def test_create_vm(self):
        HEADING()

        StopWatch.start("Create VM Started")
        test_vm = self.p.create()
        StopWatch.stop("Create VM Finished")

        assert test_vm is None
