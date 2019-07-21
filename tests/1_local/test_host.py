###############################################################
# pytest -v --capture=no  tests/1_local/test_host.py:Test_host.test_ping
# pytest -v --capture=no  tests/1_local/test_host.py
# pytest -v tests/1_local/test_host.py
###############################################################
import os

import pytest
from cloudmesh.common.util import HEADING
from cloudmesh.common3.Benchmark import Benchmark
from cloudmesh.common3.host import Host


@pytest.mark.incremental
class Test_host:

    def setup(self):
        pass

    def test_ping(self):
        HEADING()
        hosts = ['google.com', 'youtube.com', 'com']
        Benchmark.Start()
        results = Host.ping(hosts=hosts,
                           count=3,
                           processors=3)
        Benchmark.Stop()
        for result in results:
            assert result['success']

    def test_check(self):
        """
        This test only checks on host 127.0.0.1
        If wish to test successful checks, modify key, username, hosts to with your own credentials
        """
        HEADING()
        key = '~/.ssh/authorized_keys/id_rsa.pub'
        username = os.environ['USER']
        hosts = ['127.0.0.1']
        Benchmark.Start()
        result = Host.check(key=key, username=username, hosts=hosts,
                            processors=3)
        Benchmark.Stop()
        assert {'0': 0} not in result

    def test_benchmark(self):
        Benchmark.print()
