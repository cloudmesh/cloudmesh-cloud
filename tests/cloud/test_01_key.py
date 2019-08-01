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

Benchmark.debug()

KEY='test-key'

user = Config()["cloudmesh.profile.user"]
variables = Variables()

cloud = variables.parameter('cloud')

print(f"Test run for {cloud}")

if cloud is None:
    raise ValueError("cloud is not not set")

cm = CmDatabase()
provider = Provider(name=cloud)

@pytest.mark.incremental
class Test_key:

    def test_upload_key_to_database(self):
        HEADING()
        local = Key()
        Benchmark.Start()
        local.add("test-key", "ssh")
        Benchmark.Stop()

        key = cm.find_name(KEY, "key")[0]
        key['name'] == KEY

    def test_delete_keyfrom_cloud(self):
        try:
            Benchmark.Start()
            r = provider.key_delete(KEY)
            Benchmark.Stop()
        except Exception as e:
            print(e)
        print (r)

    def test_upload_key_to_cloud(self):
        key = cm.find_name(KEY, "key")[0]
        pprint(key)
        Benchmark.Start()
        r = provider.key_upload(key)
        Benchmark.Stop()
        # print ("PPP", r)

    def test_list_key_from_cloud(self):
        Benchmark.Start()
        keys = provider.keys()
        Benchmark.Stop()
        found = False
        for key in keys:
            if key['name'] == KEY:
                found = True
                break
        assert found

    def test_get__key_from_cloud(self):
        pass

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=False, tag=cloud)
