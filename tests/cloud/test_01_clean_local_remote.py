###############################################################
# pytest -v --capture=no tests/cloud/test_01_clean_remote.py
# pytest -v  tests/cloud/test_01_clean_remote.py
###############################################################

import os

import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.configuration.Config import Config
from cloudmesh.mongo.CmDatabase import CmDatabase

Benchmark.debug()

user = Config()["cloudmesh.profile.user"]
variables = Variables()

cloud = variables.parameter('cloud')

print(f"Test run for {cloud}")

if cloud is None:
    raise ValueError("cloud is not set")

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
            for key in keys:
                if cloud == 'aws':
                    key_name = key['KeyName']
                else:
                    key_name = key['name']

                r = provider.key_delete(key_name)
                print(r)
            Benchmark.Stop()
        except Exception as e:
            print(e)
            assert False

    def test_delete_all_secgroups_from_cloud(self):
        HEADING()
        try:
            if cloud == 'google':
                return
            secgroups = provider.list_secgroups()
            Benchmark.Start()
            for secgroup in secgroups:
                if cloud == 'aws':
                    groupname = secgroup['GroupName']
                # elif cloud == 'chameleon':
                elif cloud == 'oracle':
                    groupname = secgroup['_display_name']
                else:
                    groupname = secgroup['name']

                if groupname == 'default':
                    continue

                r = provider.remove_secgroup(groupname)
                print(secgroup)
            Benchmark.Stop()
        except Exception as e:
            print(e)
            assert False

    # def test_terminate_all_instances(self):
    #     HEADING()
    #     try:
    #         instances = provider.list()
    #         Benchmark.Start()
    #         for instance in instances:
    #             if cloud == 'aws':
    #                 instance_name = instance['name']
    #             elif cloud == 'chameleon':
    #                 instance_name = instance['name']
    #             r = provider.destroy(instance_name)
    #             print(r)
    #         Benchmark.Stop()
    #     except Exception as e:
    #         print(e)
    #         assert False

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=False, tag=cloud)
