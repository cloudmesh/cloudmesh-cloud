###############################################################
# pytest -v --capture=no tests/1_local/test_cms.py
# pytest -v  tests/1_local/test_cms.py
# pytest -v --capture=no  tests/1_local/test_cms.py:Test_cms.<METHIDNAME>
###############################################################
import pytest
from cloudmesh.common.Shell import Shell
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.common3.Benchmark import Benchmark
Benchmark.debug()


@pytest.mark.incremental
class TestConfig:

    def test_help(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms help", shell=True)
        Benchmark.Stop()
        VERBOSE(result)

        assert "quit" in result
        assert "clear" in result

    def test_vm(self):
        HEADING()
        Benchmark.Start()
        result = Shell.execute("cms help vm", shell=True)
        Benchmark.Stop()
        VERBOSE(result)

        assert "['sample1', 'sample2', 'sample3', 'sample18']" in result

    def test_help_again(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms help", shell=True)
        Benchmark.Stop()
        VERBOSE(result)

        assert "quit" in result
        assert "clear" in result

    """
    def test_storage(self):
        HEADING()

        result = Shell.execute("cms help storage", shell=True)

        VERBOSE(result)

        assert "storage put SOURCE DESTINATION --recursive" in result
    """

    def test_benchmark(self):
        Benchmark.print()
