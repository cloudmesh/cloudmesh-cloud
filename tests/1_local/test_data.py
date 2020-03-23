###############################################################
# pytest -v --capture=no tests/1_local/test_data.py
# pytest -v  tests/1_local/test_data.py
###############################################################
try:
    import grp
except:
    print(
        "ERROR: import grp not supported on your OS. please find altrenative to grp")

try:
    import pwd
except:
    print(
        "ERROR: import grp not supported on your OS. please find altrenative to grp")

import os

from pathlib import Path
from pprint import pprint

import pytest
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate

Benchmark.debug()

cloud = "local"


@pytest.mark.incremental
class TestDatabaseUpdate:

    def test_DatabaseUpdate(self):
        HEADING()

        file = str(Path(path_expand("~/.cloudmesh/cloudmesh.yaml")))
        cloud = "debug"

        @DatabaseUpdate()
        def info(cloud, file):
            st = os.stat(file)
            try:
                userinfo = pwd.getpwuid(os.stat(file).st_uid)
            except:
                userinfo = "windows"

            try:
                group = {
                    "name": grp.getgrgid(userinfo.pw_gid).gr_name,
                    "id": userinfo.pw_gid,
                    "members": grp.getgrgid(userinfo.pw_gid).gr_mem
                }
            except:
                group = {
                    "name": "not supported on your os, please fix this test.",
                    "id": "not supported on your os, please fix this test.",
                    "members": "not supported on your os, please fix this test.",
                }
            try:
                owner = userinfo.pw_name
            except:
                owner = "windows"

            d = {
                "cm": {
                    "kind": "file",
                    "cloud": cloud,
                    "name": f"{cloud}:{file}",
                },
                "name": f"{cloud}:{file}",
                "path": file,
                "size": st.st_size,
                "acess": str(st.st_atime),
                # needs to be same format as we  use in vms
                "modified": None,  # needs to be same format as we  use in vms
                "created": None,  # needs to be same format as we  use in vms
                "owner": owner,
                "group": group,
                "permission": {
                    "readable": os.access(file, os.R_OK),
                    "writable": os.access(file, os.W_OK),
                    "executable": os.access(file, os.X_OK)
                }

            }
            return d

        Benchmark.Start()
        i = info(cloud, file)
        Benchmark.Stop()

        pprint(i)
        path = path_expand("~/.cloudmesh/cloudmesh.yaml")
        assert i[0]['path'] == path

    def test_remove_collection(self):
        HEADING()
        cm = CmDatabase()
        Benchmark.Start()
        collection = cm.clear(collection="debug-file")
        Benchmark.Stop()

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag=cloud)


"""
class TestMongo:

    def setup(self):
        self.mongo = MongoDB()

    def test_01_MongoDBControler_Borg_test(self):
        HEADING()

        m1 = MongoDBController()

        PRINT("m1", m1.__dict__)

        m2 = MongoDBController()
        m3 = MongoDBController()

        m3.data["TEST"] = "test"

        PRINT("m1", m1.__dict__)
        PRINT("m2", m1.__dict__)
        PRINT("m3", m3.__dict__)

        assert m3.data["TEST"] == "test"
        assert m2.data["TEST"] == "test"
        assert m1.data["TEST"] == "test"

"""
"""
    def test_01_saveto(self):
        HEADING()
        d = r_dict()
        assert isinstance(d, dict)
        lst = r_list()
        assert isinstance(lst, list)

    def test_02_find(self):
        HEADING()
        doc = self.mongo.find_document("test", "name", "test-dict-1")
        assert doc is not None

    def test_03_delete(self):
        HEADING()
        old_doc = self.mongo.delete_document("test", "name", "test-dict-1")
        assert old_doc is not None

        deleted_doc = self.mongo.find_document("test", "name", "test-dict-1")
        assert deleted_doc is None
"""
