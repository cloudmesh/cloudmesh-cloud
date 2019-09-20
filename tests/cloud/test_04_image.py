###############################################################
# pytest -v --capture=no tests/cloud/test_03_image.py
# pytest -v  tests/cloud/test_03_image.py
###############################################################

import os

import pytest
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables
from cloudmesh.common3.Benchmark import Benchmark
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
class Test_Image:

    def test_empty_database(self):
        HEADING()
        Benchmark.Start()
        cm.clear(collection=f"{cloud}-falvor")
        Benchmark.Stop()

    def test_provider_image(self):
        HEADING()
        local = Key()
        Benchmark.Start()
        r = provider.images()
        Benchmark.Stop()

    def test_provider_image_update(self):
        HEADING()
        local = Key()
        Benchmark.Start()
        r = provider.images()
        Benchmark.Stop()

        cm.clear(collection=f"{cloud}-falvor")

    def test_cms_image_refresh(self):
        HEADING()
        local = Key()
        Benchmark.Start()
        os.system(f"cms image list --cloud={cloud} --refresh")
        Benchmark.Stop()

    def test_cms_image(self):
        HEADING()
        local = Key()
        Benchmark.Start()
        os.system(f"cms image list")
        Benchmark.Stop()

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=False, tag=cloud)
