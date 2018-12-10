import time
from cm4.vm.Vm import Vm
from cm4.configuration.config import Config
from cm4.common.debug import HEADING, myself

# nosetest -v --nopature tests/test_cloud_azure.py


class TestCloudAzure:

    def setup(self):
        self.config = Config()
        self.azure = Vm("azure")
        self.test_node_name = 'cm-test-vm-1'
        self.test_node_id = ''

    def _wait_and_get_state(self, name, how_long=15):
        time.sleep(how_long)
        node = self.azure.provider._get_node(name)
        return node.state if node else None

    def test_azure_005_getname(self):
        HEADING(myself())
        name = self.azure.new_name()
        assert name is not None

    def test_azure_010_create(self):
        HEADING(myself())
        vm = self.azure.create()
        assert vm is not None

    def test_azure_020_ls(self):
        HEADING(myself())
        ls_results = self.azure.list()
        assert isinstance(ls_results, list)

    def test_azure_030_suspend(self):
        HEADING(myself())
        self.azure.suspend(name=self.test_node_name)
        state = self._wait_and_get_state(self.test_node_name)
        assert state == 'stopped'
        # assert state == 'paused'

    def test_azure_050_stop(self):
        HEADING(myself())
        self.azure.stop(name=self.test_node_name)
        state = self._wait_and_get_state(self.test_node_name, 30)
        assert state == 'stopped'

    def test_azure_060_start(self):
        HEADING(myself())
        self.azure.start(name=self.test_node_name)
        state = self._wait_and_get_state(self.test_node_name, 30)
        assert state == 'running'

    def test_azure_070_destroy(self):
        HEADING(myself())
        self.azure.destroy(name=self.test_node_name)

    # def test_azure_create_network(self):
    #     HEADING(myself())
    #     self.azure._create_network("cmnet")

    # def test_azure_list_volumes(self):
    #     HEADING(myself())
    #     vols = self.azure.list_volumes()

    # def test_azure_delete_network(self):
    #     HEADING(myself())
    #     self.azure._ex_delete_network("cmnetwork")

    # def test_azure_get_node(self):
    #     HEADING(myself())
    #     vm = self.azure._get_node(name=self.test_node_name)
    #     assert vm is not None

    # def test_azure_run(self):
    #     HEADING(myself())
    #     cmd = "lsb_release -a"
    #     res = self.azure.run(name=self.test_node_name, cmd)
    #     # getting output
    #     # https://stackoverflow.com/questions/38152873/how-can-i-get-the-output-of-a-customscriptextenstion-when-using-azure-resource-m
    #
    #     assert res is not None
