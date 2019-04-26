###############################################################
# pip install .; npytest -v --capture=no  tests/test_check.py:Test_check.test_001
# pytest -v --capture=no  tests/test_check.py
# pytest -v tests/test_check.py
###############################################################
from __future__ import print_function

import getpass

from cloudmesh.common3.Shell import Shell as Shell3
from cloudmesh.common.util import HEADING
import pytest

@pytest.mark.incremental
class Test_check:

    def setup(self):
        pass

    def test_001(self):
        """
        This test only checks on host 0.0.0.0
        If wish to test successful checks, modify key, username, hosts to with your own credentials
        """
        HEADING()
        key = ''
        username = 'root'
        hosts = ['0']
        result = Shell3.checks(key=key, username=username, hosts=hosts, processors=3)
        assert {'0': 0} not in result
