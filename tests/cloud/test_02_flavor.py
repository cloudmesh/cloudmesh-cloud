###############################################################
# pytest -v --capture=no tests/test_01_key/test_key.py
# pytest -v  tests/test_01_key/test_key.py
###############################################################
from pprint import pprint

import pytest
from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import HEADING
from cloudmesh.common3.Benchmark import Benchmark
from cloudmesh.management.configuration.SSHkey import SSHkey
from cloudmesh.configuration.Config import Config
from cloudmesh.key.Key import Key
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.common.variables import Variables
from cloudmesh.compute.vm.Provider import Provider
import os

Benchmark.debug()

user = Config()["cloudmesh.profile.user"]
variables = Variables()

cloud = variables.parameter('cloud')
variables["refresh"] = 'False'

print(f"Test run for {cloud}")

if cloud is None:
    raise ValueError("cloud is not not set")

cm = CmDatabase()
provider = Provider(name=cloud)

@pytest.mark.incremental
class Test_Flavor:


    def test_empty_database(self):
        HEADING()
        Benchmark.Start()
        cm.clear(collection=f"{cloud}-falvor")
        Benchmark.Stop()


    def test_provider_flavor(self):
        HEADING()
        local = Key()
        Benchmark.Start()
        r = provider.flavors()
        Benchmark.Stop()

    def test_provider_flavor_update(self):
        HEADING()
        local = Key()
        Benchmark.Start()
        r = provider.flavors()
        Benchmark.Stop()

        cm.clear(collection=f"{cloud}-falvor")



    def test_cms_flavor_refresh(self):
        HEADING()
        local = Key()
        Benchmark.Start()
        os.system(f"cms flavor list --cloud={cloud} --refresh")
        Benchmark.Stop()



    def test_cms_flavor(self):
        HEADING()
        local = Key()
        Benchmark.Start()
        os.system(f"cms flavor list")
        Benchmark.Stop()

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=False, tag=cloud)
