###############################################################
# pip install .; pytest -v --capture=no  tests/aws/test_aws..py::Test_aws.test_001
# pytest -v --capture=no tests/aws/test_aws.py
# pytest -v  tests/aws/test_aws.py
###############################################################

import time

import pytest
from cloudmesh.common.util import HEADING
from cloudmesh.configuration.Config import Config
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.common.Benchmark import Benchmark

Benchmark.debug()

cloud = "aws"


@pytest.mark.incremental
class TestCloudAws:

    def setup(self):
        self.config = Config()
        self.provider = Provider(name="aws")
        self.test_node_name = 'test1'
        self.test_node_id = ''

    def _wait_and_get_state(self, name, how_long=15):
        time.sleep(how_long)
        node = self.provider.provider.driver._get_node(name)
        return node.state if node else None

    def test_create(self):
        HEADING()
        vm = self.provider.create(self.test_node_name)
        assert vm is not None

    def test_list(self):
        HEADING()
        results = self.provider.list()
        assert isinstance(results, list)

    def test__info(self):
        HEADING()
        info = self.provider.info(self.test_node_name)
        assert info is not None

    def test_suspend(self):
        HEADING()
        self.provider.suspend(name=self.test_node_name)
        # state = self._wait_and_get_state(self.test_node_name)
        # assert state == 'paused'

    def test_stop(self):
        HEADING()
        self.provider.stop(name=self.test_node_name)
        state = self._wait_and_get_state(self.test_node_name, 30)
        assert state == 'deallocating' or state == 'stopped'

    def test_start(self):
        HEADING()
        self.provider.start(name=self.test_node_name)
        state = self._wait_and_get_state(self.test_node_name, 30)
        assert state == 'running'

    def test_destroy(self):
        HEADING()
        self.provider.destroy(name=self.test_node_name)

    def test_list_sizes(self):
        HEADING()
        vols = self.provider.provider.list_sizes()
        assert vols is not None

    def test_benchmark(self):
        Benchmark.print(csv=True, sysinfo=False, tag=cloud)
