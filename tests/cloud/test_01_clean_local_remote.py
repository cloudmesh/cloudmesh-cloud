###############################################################
# pytest -v --capture=no tests/cloud/test_01_clean_remote.py
# pytest -v  tests/cloud/test_01_clean_remote.py
###############################################################
from pprint import pprint

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

print(f"Test run for {cloud}")

if cloud is None:
    raise ValueError("cloud is not not set")

cm = CmDatabase()
provider = Provider(name=cloud)


@pytest.mark.incremental
class Test_Clean_Local_Remote:

    def test_cms_init(self):
        HEADING()
        Benchmark.Start()
        result = os.system(f"cms init")
        Benchmark.Stop()

    def test_delete_all_keys_from_cloud(self):
        HEADING()
        try:
            keys = provider.keys()
            Benchmark.Start()
            if cloud == 'aws':
                for key in keys:
                    r = provider.key_delete(key['KeyName'])
                    print(r)
            else:
                raise NotImplementedError
            Benchmark.Stop()
        except Exception as e:
            print(e)
            assert False

    def test_delete_all_secgroups_from_cloud(self):
        HEADING()
        try:
            secgroups = provider.list_secgroups()
            Benchmark.Start()
            if cloud == 'aws':
                for secgroup in secgroups:
                    r = provider.remove_secgroup(secgroup['GroupName'])
                    print(secgroup)
            else:
                raise NotImplementedError
            Benchmark.Stop()
        except Exception as e:
            print(e)
            assert False

    def test_terminate_all_instances(self):
        HEADING()
        try:
            instances = provider.list()
            Benchmark.Start()
            if cloud == 'aws':
                for instance in instances:
                    r = provider.destroy(instance['name'])
                    print(r)
            else:
                raise NotImplementedError
            Benchmark.Stop()
        except Exception as e:
            print(e)
            assert False

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=False, tag=cloud)
