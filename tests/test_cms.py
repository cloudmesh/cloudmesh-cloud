###############################################################
# pytest -v --capture=no tests/test_cms.py
# pytest -v  tests/test_cms.py
# pytest -v --capture=no -v --nocapture tests/test_cms.py:Test_cms.<METHIDNAME>
###############################################################
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.util import HEADING
from pprint import pprint
import textwrap
import oyaml as yaml
import munch
import re

from cloudmesh.common.Shell import Shell
from cloudmesh.DEBUG import VERBOSE
import pytest

@pytest.mark.incremental
class TestConfig:

    def test_01_help(self):
        HEADING()

        result = Shell.execute("cms help", shell=True)

        VERBOSE(result)

        assert "quit" in result
        assert "clear" in result

    def test_01_vm(self):
        HEADING()

        result = Shell.execute("cms help vm", shell=True)

        VERBOSE(result)

        assert "['sample1', 'sample2', 'sample3', 'sample18']" in result

    def test_01_storage(self):
        HEADING()

        result = Shell.execute("cms help storage", shell=True)

        VERBOSE(result)

        assert "storage put SOURCE DESTINATION --recursive" in result
