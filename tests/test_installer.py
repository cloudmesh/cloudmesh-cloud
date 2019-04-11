###############################################################
# pip install .; pytest -v --capture=no -v --nocapture tests/test_installer.py:Test_installer.test_001
# pytest -v --capture=no tests/test_installerr.py
# pytest -v  tests/test_installer.py
###############################################################

from __future__ import print_function
import shutil

import os
import pytest
from cloudmesh_installer.install.test import readfile, run


@pytest.mark.incremental
class Test_configdict:

    def test_create_dir(self):
        path = "tmp"
        try:
            os.mkdir(path)
        except OSError:
            print(f"Creation of the directory {path} failed")
        else:
            print(f"Successfully created the directory {path}")

        assert True

    def test_info(self):
        cmd = "cloudmesh-installer info"
        result = run(cmd)
        print(result)
        assert "Package" in str(result)

    def test_clone_cloud(self):
        cmd = "cd tmp; cloudmesh-installer git clone cloud"
        result = run(cmd)
        print(result)
        assert os.path.isdir("tmp/cloudmesh-cmd5")

    def test_install_cms(self):
        cmd = "cd tmp; cloudmesh-installer install cms -e"
        result = run(cmd)
        print(result)
        assert os.path.isdir("tmp/cloudmesh-cmd5/cloudmesh_cmd5.egg-info")

    def test_cms_help(self):
        cmd = "cms help"
        result = run(cmd)
        print(result)
        assert "quit" in result

    def test_cms_info(self):
        cmd = "cms info"
        result = run(cmd)
        print(result)
        assert "cloudmesh.common" in result

    def test_cms_verion(self):
        cmd = "cms version"
        result = run(cmd)
        print(result)
        assert "cloudmesh.common" in result

    def test_install_cloud(self):
        cmd = "cd tmp; cloudmesh-installer install cloud -e"
        result = run(cmd)
        print(result)
        assert os.path.isdir("tmp/cloudmesh-cloud/cloudmesh_cloud.egg-info")

    def test_cms_info(self):
        cmd = "cms info"
        result = run(cmd)
        print(result)
        assert "cloudmesh.cloud" in result

    def test_cms_help(self):
        cmd = "cms help"
        result = run(cmd)
        print(result)
        assert "vm" in result

    def test_cms_info(self):
        cmd = "cms info"
        result = run(cmd)
        print(result)
        assert "cloudmesh.common" in result

    def test_cms_verion(self):
        cmd = "cms version"
        result = run(cmd)
        print(result)
        assert "cloudmesh.common" in result


class other:
    def test_delete_dir(self):
        path = "tmp"
        shutil.rmtree(path)
        assert True
