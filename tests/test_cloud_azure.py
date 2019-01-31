import time
from cloudmesh.draft.vm.api.Vm import Vm
from cloudmesh.management.configuration.config import Config
from cloudmesh.management.debug import HEADING, myself

# nosetest -v --nopature tests/test_cloud_azure.py


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
        HEADING(myself())
        vm = self.azure.create(self.test_node_name)
        assert vm is not None

    def test_azure_020_nodes(self):
        HEADING(myself())
        results = self.azure.nodes()
        assert isinstance(results, list)

    def test_azure_025_info(self):
        HEADING(myself())
        info = self.azure.info(self.test_node_name)
        assert info is not None

    def test_azure_030_suspend(self):
        HEADING(myself())
        self.azure.suspend(name=self.test_node_name)
        state = self._wait_and_get_state(self.test_node_name)
        assert state == 'stopped'

    def test_azure_050_start(self):
        HEADING(myself())
        self.azure.start(name=self.test_node_name)
        state = self._wait_and_get_state(self.test_node_name, 30)
        assert state == 'running'

    def test_azure_060_stop(self):
        HEADING(myself())
        self.azure.stop(name=self.test_node_name)
        state = self._wait_and_get_state(self.test_node_name, 30)
        assert state == 'deallocating' or state == 'stopped'

    def test_azure_070_destroy(self):
        HEADING(myself())
        self.azure.destroy(name=self.test_node_name)

    def test_azure_100_list_sizes(self):
        HEADING(myself())
        vols = self.azure.provider.list_sizes()
        assert vols is not None
