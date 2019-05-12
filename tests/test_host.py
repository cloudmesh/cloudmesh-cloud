###############################################################
# pytest -v --capture=no  tests/test_host.py:Test_host.test_ping
# pytest -v --capture=no  tests/test_host.py
# pytest -v tests/test_host.py
###############################################################
from cloudmesh.common3.host import Host
from cloudmesh.common.util import HEADING
import pytest
import os


@pytest.mark.incremental
class Test_host:

    def setup(self):
        pass

    def test_ping(self):
        HEADING()
        result = Host.ping(hosts=['google.com', 'youtube.com', 'com'], count=3, processors=3)
        assert {'google.com': 0} in result
        assert {'youtube.com': 0} in result
        assert {'com': 0} not in result


    def test_check(self):
        """
        This test only checks on host 127.0.0.1
        If wish to test successful checks, modify key, username, hosts to with your own credentials
        """
        HEADING()
        key = '~/.ssh/authorized_keys/id_rsa.pub'
        username = os.environ['USER']
        hosts = ['127.0.0.1']
        result = Host.check(key=key, username=username, hosts=hosts, processors=3)
        assert {'0': 0} not in result
