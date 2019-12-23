###############################################################
# pytest -v --capture=no tests/cloud/test_02_flavor.py
# pytest -v  tests/cloud/test_02_flavor.py
###############################################################

import os

import pytest
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.configuration.Config import Config
from cloudmesh.key.Key import Key
from cloudmesh.mongo.CmDatabase import CmDatabase

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
        r = provider.flavors(n_results=30)
        Benchmark.Stop()

    def test_provider_flavor_update(self):
        HEADING()
        local = Key()
        Benchmark.Start()
        r = provider.flavors(n_results=30)
        Benchmark.Stop()

        cm.clear(collection=f"{cloud}-falvor")

    def test_cms_flavor_refresh(self):
        HEADING()
        local = Key()
        Benchmark.Start()
        if cloud == 'aws':
            query = '''{\
                \\\"Type\\\":\\ \\\"TERM_MATCH\\\"\\,\\ \
                \\\"Field\\\":\\ \\\"instancesku\\\"\\,\\ \
                \\\"Value\\\":\\ \\\"3MFG4YWWT6SPWHET\\\"\
                }'''
            system_cmd = \
                f"cms flavor list --cloud={cloud} --query={query} --refresh \
                > flavor-{cloud}.log"
            os.system(system_cmd)
        else:
            os.system(
                f"cms flavor list --cloud={cloud} --refresh \
                > flavor-{cloud}.log"
            )
        Benchmark.Stop()

    def test_cms_flavor(self):
        HEADING()
        local = Key()
        Benchmark.Start()
        os.system(f"cms flavor list > flavor-mongo.log")
        Benchmark.Stop()

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)
