###############################################################
# pip install .; pytest -v --capture=no  tests/aws/test_aws.py:Test_aws.test_001
# pytest -v --capture=no tests/aws/test_aws.py
# pytest -v  tests/aws/test_aws.py
###############################################################

import time

import pytest
from cloudmesh.common.util import HEADING
from cloudmesh.management.configuration.config import Config

#
# TODO: THIS IS A BUG, the deprecated api shoudl not be used
#
from deprecated.draft.vm.api.Vm import Vm


@pytest.mark.incremental
class TestCloudAws:

    def setup(self):
        self.config = Config()
        self.aws = Vm("aws")
        self.test_node_name = 'test1'
        self.test_node_id = ''

    def _wait_and_get_state(self, name, how_long=15):
        time.sleep(how_long)
        node = self.aws.provider.driver._get_node(name)
        return node.state if node else None

    def test_aws_010_create(self):
        HEADING()
        vm = self.aws.create(self.test_node_name)
        assert vm is not None

    def test_aws_020_nodes(self):
        HEADING()
        results = self.aws.nodes()
        assert isinstance(results, list)

    def test_aws_025_info(self):
        HEADING()
        info = self.aws.info(self.test_node_name)
        assert info is not None

    def test_aws_030_suspend(self):
        HEADING()
        self.aws.suspend(name=self.test_node_name)
        # state = self._wait_and_get_state(self.test_node_name)
        # assert state == 'paused'

    def test_aws_050_stop(self):
        HEADING()
        self.aws.stop(name=self.test_node_name)
        state = self._wait_and_get_state(self.test_node_name, 30)
        assert state == 'deallocating' or state == 'stopped'

    def test_aws_060_start(self):
        HEADING()
        self.aws.start(name=self.test_node_name)
        state = self._wait_and_get_state(self.test_node_name, 30)
        assert state == 'running'

    def test_aws_070_destroy(self):
        HEADING()
        self.aws.destroy(name=self.test_node_name)

    def test_aws_100_list_sizes(self):
        HEADING()
        vols = self.aws.provider.list_sizes()
        assert vols is not None
