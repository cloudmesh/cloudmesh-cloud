import time
from cloudmesh.draft.vm.api.Vm import Vm
from cloudmesh.management.configuration.config import Config
from cloudmesh.management.debug import HEADING, myself

# nosetest -v --nopature tests/test_cloud_aws.py


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
        HEADING(myself())
        vm = self.aws.create(self.test_node_name)
        assert vm is not None

    def test_aws_020_nodes(self):
        HEADING(myself())
        results = self.aws.nodes()
        assert isinstance(results, list)

    def test_aws_025_info(self):
        HEADING(myself())
        info = self.aws.info(self.test_node_name)
        assert info is not None

    def test_aws_030_suspend(self):
        HEADING(myself())
        self.aws.suspend(name=self.test_node_name)
        # state = self._wait_and_get_state(self.test_node_name)
        # assert state == 'paused'

    def test_aws_050_stop(self):
        HEADING(myself())
        self.aws.stop(name=self.test_node_name)
        state = self._wait_and_get_state(self.test_node_name, 30)
        assert state == 'deallocating' or state == 'stopped'

    def test_aws_060_start(self):
        HEADING(myself())
        self.aws.start(name=self.test_node_name)
        state = self._wait_and_get_state(self.test_node_name, 30)
        assert state == 'running'

    def test_aws_070_destroy(self):
        HEADING(myself())
        self.aws.destroy(name=self.test_node_name)

    def test_aws_100_list_sizes(self):
        HEADING(myself())
        vols = self.aws.provider.list_sizes()
        assert vols is not None
