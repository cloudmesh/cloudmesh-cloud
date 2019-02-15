from pprint import pprint
import time
import subprocess
import sys
from cloudmesh.common.util import HEADING
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.util import path_expand
from pathlib import Path
import os
from pprint import pprint
import pwd
import grp
from  cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate

# nosetest -v --nopature
# nosetests -v --nocapture tests/test_data.py

class test_data:

    def setup(self):
        pass

    def test_01_stat(self):
        HEADING()

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
                "acess": str(st.st_atime), # needs to be same format as we  use in vms
                "modified": None, # needs to be same format as we  use in vms
                "created": None, # needs to be same format as we  use in vms
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
            return [d]

        i = info(file)

        pprint (i)


        assert i['path']== '/Users/grey/.cloudmesh/cloudmesh4.yaml'
