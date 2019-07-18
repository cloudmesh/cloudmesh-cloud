###############################################################
# pytest -v --capture=no tests/1_basic/test_data.py
# pytest -v  tests/1_basic/test_data.py
# pytest -v --capture=no  tests/1_basic/test_data.py:Test_data.<METHIDNAME>
###############################################################
from pprint import pprint

import pytest
from cloudmesh.common.util import HEADING, banner
from cloudmesh.common.util import path_expand
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
from pathlib import Path
import os
import pwd
import grp
from cloudmesh.common3.Benchmark import Benchmark

banner("START")

@pytest.mark.incremental
class TestDatabaseUpdate:

    def test_DatabaseUpdate(self):
        HEADING()

        print ("AAA")
        file = str(Path(path_expand("~/.cloudmesh/cloudmesh4.yaml")))

        @DatabaseUpdate()
        def info(file):
            st = os.stat(file)
            userinfo = pwd.getpwuid(os.stat(file).st_uid)

            d = {
                "kind": "file",
                "cloud": "local",
                "name": "{cloud}:{file}".format(cloud="local", file=file),
                "path": file,
                "size": st.st_size,
                "acess": str(st.st_atime),
                # needs to be same format as we  use in vms
                "modified": None,  # needs to be same format as we  use in vms
                "created": None,  # needs to be same format as we  use in vms
                "owner": userinfo.pw_name,
                "group": {
                    "name": grp.getgrgid(userinfo.pw_gid).gr_name,
                    "id": userinfo.pw_gid,
                    "members": grp.getgrgid(userinfo.pw_gid).gr_mem
                },
                "permission": {
                    "readable": os.access(file, os.R_OK),
                    "writable": os.access(file, os.W_OK),
                    "executable": os.access(file, os.X_OK)
                }

            }
            return d

        Benchmark.Start()
        i = info(file)
        Benchmark.Stop()

        pprint(i)

        assert i['path'] == '/Users/grey/.cloudmesh/cloudmesh4.yaml'


    def test_benchmark(self):
        Benchmark.print()
