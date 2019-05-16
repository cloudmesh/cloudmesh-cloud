###############################################################
# pytest -v --capture=no benchmark/test_cms.py
# pytest -v  benchmark/test_cms.py
# pytest -v --capture=no benchmark/test_cms.py:Test_cms.<METHIDNAME>
###############################################################

import pytest
from cloudmesh.common.DEBUG import VERBOSE
from cloudmesh.common.Shell import Shell
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.util import HEADING


@pytest.mark.incremental
class TestConfig:

    def test_help(self):
        HEADING()

        StopWatch.start("cms help")
        result = Shell.execute("cms help", shell=True)
        StopWatch.stop("cms help")

        VERBOSE(result)

        assert "quit" in result
        assert "clear" in result

    def test_vm(self):
        HEADING()

        StopWatch.start("cms help vm")
        result = Shell.execute("cms help vm", shell=True)
        StopWatch.stop("cms help vm")

        VERBOSE(result)

        assert "['sample1', 'sample2', 'sample3', 'sample18']" in result

    def test_storage(self):
        HEADING()

        StopWatch.start("cms help vm")
        result = Shell.execute("cms help vm", shell=True)
        StopWatch.stop("cms help vm")

        VERBOSE(result)

        assert "vm" in result

    def test_results(self):
        HEADING()

        StopWatch.benchmark()
