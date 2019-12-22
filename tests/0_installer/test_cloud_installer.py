###############################################################
# pip install .; pytest -v --capture=no tests/1_installer/test_cloud_installer.py:Test_cloud_installer.test_001
# pytest -v --capture=no tests/1_installer/test_cloud_installerr.py
# pytest -v  tests/1_installer/test_cloud_installer.py
###############################################################

import os
import shutil

import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh_installer.install.util import run
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING

Benchmark.debug()

cloud = "local"

@pytest.mark.incremental
class Test_cloud_installer:

    def test_create_dir(self):
        HEADING()
        path = "tmp"
        try:
            os.mkdir(path)
        except OSError:
            print(f"Creation of the directory {path} failed")
        else:
            print(f"Successfully created the directory {path}")

        assert True

    def test_info(self):
        HEADING()
        cmd = "cloudmesh-installer info"
        Benchmark.Start()
        result = run(cmd)
        Benchmark.Stop()
        print(result)
        assert "Package" in str(result)

    def test_clone_cloud(self):
        HEADING()
        cmd = "cd tmp; cloudmesh-installer git clone cloud"
        Benchmark.Start()
        result = run(cmd)
        Benchmark.Stop()
        print(result)
        assert os.path.isdir("tmp/cloudmesh-cmd5")

    def test_install_cms(self):
        HEADING()
        cmd = "cd tmp; cloudmesh-installer install cms -e"
        Benchmark.Start()
        result = run(cmd)
        Benchmark.Stop()
        print(result)
        assert os.path.isdir("tmp/cloudmesh-cmd5/cloudmesh_cmd5.egg-info")

    def test_cms_help(self):
        HEADING()
        cmd = "cms help"
        Benchmark.Start()
        result = run(cmd)
        Benchmark.Stop()
        print(result)
        assert "quit" in result

    def test_cms_info_common(self):
        HEADING()
        cmd = "cms info"
        Benchmark.Start()
        result = run(cmd)
        Benchmark.Stop()
        print(result)
        assert "cloudmesh.common" in result

    def test_install_cloud(self):
        HEADING()
        cmd = "cd tmp; cloudmesh-installer install cloud -e"
        Benchmark.Start()
        result = run(cmd)
        Benchmark.Stop()
        print(result)
        assert os.path.isdir("tmp/cloudmesh-cloud/cloudmesh_cloud.egg-info")

    def test_cms_info_cloud(self):
        HEADING()
        cmd = "cms info"
        result = run(cmd)
        print(result)
        assert "cloudmesh.cloud" in result

    def test_cms_vm(self):
        HEADING()
        cmd = "cms help"
        Benchmark.Start()
        result = run(cmd)
        Benchmark.Stop()
        print(result)
        assert "vm" in result

    def test_cms_info(self):
        HEADING()
        cmd = "cms info"
        Benchmark.Start()
        result = run(cmd)
        Benchmark.Stop()
        print(result)
        assert "cloudmesh.common" in result

    def test_cms_version(self):
        HEADING()
        cmd = "cms version"
        Benchmark.Start()
        result = run(cmd)
        Benchmark.Stop()
        print(result)
        assert "cloudmesh.common" in result

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, tag=cloud)


class other:
    def test_delete_dir(self):
        path = "tmp"
        shutil.rmtree(path)
        assert True
