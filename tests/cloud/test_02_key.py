###############################################################
# pytest -v --capture=no tests/cloud/test_02_key.py
# pytest -v  tests/cloud/test_02_key.py
# pytest -v --capture=no tests/cloud/test_02_key.py::Test_Key::test_upload_key_to_database
###############################################################
import os
from pprint import pprint

import pytest
from cloudmesh.common import VERBOSE
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.configuration.Config import Config
from cloudmesh.key.Key import Key
from cloudmesh.mongo.CmDatabase import CmDatabase

Benchmark.debug()

user = Config()["cloudmesh.profile.user"]
variables = Variables()

KEY = "test-key"
cloud = variables.parameter('cloud')

print(f"Test run for {cloud} on key {KEY}")

if cloud is None:
    raise ValueError("cloud is not not set")

cm = CmDatabase()
provider = Provider(name=cloud)


@pytest.mark.incremental
class Test_Key:

    def test_clear_local_database(self):
        HEADING()
        Benchmark.Start()
        cm.clear(collection=f"local-key")
        Benchmark.Stop()
        assert True

    def test_clear_cloud_database(self):
        HEADING()
        Benchmark.Start()
        cm.clear(collection=f"{cloud}-key")
        Benchmark.Stop()
        assert True

    def test_upload_key_to_database(self):
        HEADING()

        local = Key()
        pprint(local)
        Benchmark.Start()
        local.add(KEY, "ssh")
        Benchmark.Stop()

        key = cm.find_name(KEY, "key")[0]

        assert key is not None

    def test_upload_key_to_cloud(self):
        HEADING()
        if cloud == 'azure':
            # todo: implement this
            return

        if cloud == 'aws':
            all_keys = cm.find_all_by_name(KEY, "key")
            for k in all_keys:
                if 'public_key' in k.keys():
                    key = k
                    break
        else:
            key = cm.find_name(KEY, "key")[0]
        VERBOSE(key)
        Benchmark.Start()
        r = provider.key_upload(key)
        Benchmark.Stop()
        # print ("PPP", r)

    def test_list_key_from_cloud(self):
        HEADING()
        Benchmark.Start()
        keys = provider.keys()
        Benchmark.Stop()

        if cloud in ['azure', 'oracle']:
            VERBOSE(f"{cloud} does not support key list!")
            return

        for key in keys:
            if key['name'] == KEY:
                found = True
                break

        assert found

    def test_delete_key_from_cloud(self):
        HEADING()
        try:
            Benchmark.Start()
            r = provider.key_delete(KEY)
            Benchmark.Stop()
            print(r)
        except Exception as e:
            print(e)

    def test_get_key_from_cloud(self):
        HEADING()
        pass

    def test_key_delete(self):
        HEADING()
        Benchmark.Start()
        self.test_clear_cloud_database()
        Benchmark.Stop()

    def test_cms_local(self):
        HEADING()
        Benchmark.Start()
        os.system("cms key add")
        os.system("cms key list > key-local.log")
        Benchmark.Stop()

    def test_cms_cloud(self):
        HEADING()
        self.test_clear_cloud_database()

        Benchmark.Start()
        os.system(f"cms key upload --cloud={cloud}")
        os.system(f"cms key list --cloud={cloud} > key-{cloud}.log")
        #os.system(f"cms key delete {KEY} --cloud={cloud}")
        Benchmark.Stop()

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)
