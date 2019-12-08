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

Benchmark.debug()


@pytest.mark.incremental
class Test_cloud_installer:

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
        Benchmark.Start()
        result = run(cmd)
        Benchmark.Stop()
        print(result)
        assert "Package" in str(result)

    def test_clone_cloud(self):
        cmd = "cd tmp; cloudmesh-installer git clone cloud"
        Benchmark.Start()
        result = run(cmd)
        Benchmark.Stop()
        print(result)
        assert os.path.isdir("tmp/cloudmesh-cmd5")

    def test_install_cms(self):
        cmd = "cd tmp; cloudmesh-installer install cms -e"
        Benchmark.Start()
        result = run(cmd)
        Benchmark.Stop()
        print(result)
        assert os.path.isdir("tmp/cloudmesh-cmd5/cloudmesh_cmd5.egg-info")

    def test_cms_help(self):
        cmd = "cms help"
        Benchmark.Start()
        result = run(cmd)
        Benchmark.Stop()
        print(result)
        assert "quit" in result

    def test_cms_info_common(self):
        cmd = "cms info"
        Benchmark.Start()
        result = run(cmd)
        Benchmark.Stop()
        print(result)
        assert "cloudmesh.common" in result

    def test_install_cloud(self):
        cmd = "cd tmp; cloudmesh-installer install cloud -e"
        Benchmark.Start()
        result = run(cmd)
        Benchmark.Stop()
        print(result)
        assert os.path.isdir("tmp/cloudmesh-cloud/cloudmesh_cloud.egg-info")

    def test_cms_info_cloud(self):
        cmd = "cms info"
        result = run(cmd)
        print(result)
        assert "cloudmesh.cloud" in result

    def test_cms_vm(self):
        cmd = "cms help"
        Benchmark.Start()
        result = run(cmd)
        Benchmark.Stop()
        print(result)
        assert "vm" in result

    def test_cms_info(self):
        cmd = "cms info"
        Benchmark.Start()
        result = run(cmd)
        Benchmark.Stop()
        print(result)
        assert "cloudmesh.common" in result

    def test_cms_version(self):
        cmd = "cms version"
        Benchmark.Start()
        result = run(cmd)
        Benchmark.Stop()
        print(result)
        assert "cloudmesh.common" in result

    def test_benchmark(self):
        Benchmark.print()


class other:
    def test_delete_dir(self):
        path = "tmp"
        shutil.rmtree(path)
        assert True
