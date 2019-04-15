###############################################################
#
# to find the subscription id go to
#
# https://portal.azure.com/#blade/Microsoft_Azure_Billing/BillingMenuBlade/Subscriptions
#
###############################################################
# pip install .; pytest -v --capture=no -v --nocapture tests/test_aws.py:Test_aws.test_001
# pytest -v --capture=no tests/test_aws.py
# pytest -v  tests/test_aws.py
###############################################################

from __future__ import print_function

import time

import pytest
from cloudmesh.common.util import HEADING
from cloudmesh.management.configuration.config import Config

#
# TODO: THIS IS A BUG, the deprecated api shoudl not be used
#
from deprecated.draft.vm.api.Vm import Vm
import pytest

@pytest.mark.incremental
class TestCloudAzure:

    def setup(self):
        self.config = Config()
        self.azure = Vm("azure")
        self.test_node_name = 'test1'
        self.test_node_id = ''

    def _wait_and_get_state(self, name, how_long=15):
        time.sleep(how_long)
        node = self.azure.provider.driver._get_node(name)
        return node.state if node else None

    def test_azure_010_create(self):
        HEADING()
        vm = self.azure.create(self.test_node_name)
        assert vm is not None

    def test_azure_020_nodes(self):
        HEADING()
        results = self.azure.nodes()
        assert isinstance(results, list)

    def test_azure_025_info(self):
        HEADING()
        info = self.azure.info(self.test_node_name)
        assert info is not None

    def test_azure_030_suspend(self):
        HEADING()
        self.azure.suspend(name=self.test_node_name)
        state = self._wait_and_get_state(self.test_node_name)
        assert state == 'stopped'

    def test_azure_050_start(self):
        HEADING()
        self.azure.start(name=self.test_node_name)
        state = self._wait_and_get_state(self.test_node_name, 30)
        assert state == 'running'

    def test_azure_060_stop(self):
        HEADING()
        self.azure.stop(name=self.test_node_name)
        state = self._wait_and_get_state(self.test_node_name, 30)
        assert state == 'deallocating' or state == 'stopped'

    def test_azure_070_destroy(self):
        HEADING()
        self.azure.destroy(name=self.test_node_name)

    def test_azure_100_list_sizes(self):
        HEADING()
        vols = self.azure.provider.list_sizes()
        assert vols is not None
