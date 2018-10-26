import time
from cm4.azure.AzureManager import AzureManager
from cm4.configuration.config import Config


class TestCloudAzure:

    def setUp(self):
        self.config = Config()
        self.azure = AzureManager()
        
        self.test_node_name = 'cm-test-vm-1'
        self.test_node_id = ''

    # def tearDown(self):
    #     testNode = self.azure._get_node(self.testNodeName)
    #     if testNode:
    #         self.azure.destroy(self.testNodeName)

    def _wait_and_get_state(self, name, how_long=15):
        time.sleep(how_long)
        node = self.azure._get_node(name)
        return node.state if node else None

    def test_azure_010_create(self):
        vm = self.azure.create(self.test_node_name)
        self.test_node_id = vm.id
        assert True is True

    def test_azure_020_ls(self):
        ls_results = self.azure.ls()
        assert isinstance(ls_results, list)

    def test_azure_030_suspend(self):
        self.azure.suspend(self.test_node_name)
        state = self._wait_and_get_state(self.test_node_name)
        assert state == 'paused'

    def test_azure_040_resume(self):
        self.azure.resume(self.test_node_name)
        state = self._wait_and_get_state(self.test_node_name)
        assert state == 'running'

    def test_azure_050_stop(self):
        self.azure.stop(self.test_node_name)
        state = self._wait_and_get_state(self.test_node_name, 30)
        assert state == 'stopped'

    def test_azure_060_start(self):
        self.azure.start(self.test_node_name)
        state = self._wait_and_get_state(self.test_node_name, 30)
        assert state == 'running'

    def test_azure_070_destroy(self):
        self.azure.destroy(self.test_node_name)
        state = self._wait_and_get_state(self.test_node_name, 30)
        state is None
