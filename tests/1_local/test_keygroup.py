###############################################################
# pytest -v --capture=no tests/test_keygroup.py
# pytest -v  tests/test_keygroup.py
###############################################################

#import pytest
import os
from cloudmesh.common.variables import Variables
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.configuration.Config import Config
from cloudmesh.mongo.CmDatabase import CmDatabase
# import pytest
import os

from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.variables import Variables
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.configuration.Config import Config
from cloudmesh.mongo.CmDatabase import CmDatabase

Benchmark.debug()


user = Config()["cloudmesh.profile.user"]
variables = Variables()

KEY = "test-keygroup"
cloud = variables.parameter('cloud')

print(f"Test run for {cloud} on key {KEY}")

if cloud is None:
    raise ValueError("cloud is not not set")

cm = CmDatabase()
provider = Provider(name=cloud)

#@pytest.mark.incremental
class Test_Keygroup:

    def test_create_keys(self):
        n = 5
        for i in range(0, n):
            name = f"test_id_rsa{i}"
            command = f"ssh-keygen -f $HOME/.ssh/{name}"
            os.system(command)
            # assert os.path.isfile(name)


    # create test for all other functions

    # create test for adding key to group
    def test_add_key_to_keygroup_database(self):
        n = 5
        keygroup = "testKeyGroup"
        for i in range(0, n):
            name = f"test_id_rsa{i}"
            command = f"cms keygroup add $HOME/.ssh/{name}"
            os.system(command)
    """
    def test_upload_key_to_database(self):
        HEADING()
        local = Key()
        pprint(local)
        Benchmark.Start()
        local.add(KEY, "ssh")
        Benchmark.Stop()

        key = cm.find_name(KEY, "key")[0]
        key['name'] == KEY

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
        pprint(key)
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

        found = False
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
        cm.clear(collection=f"local-key")
        try:
            r = provider.key_delete(KEY)
        except:
            pass

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)

    """
    def test_list(self):
        #os.system("cms keygroup add ")
        os.system("cms key group list")
