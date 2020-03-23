###############################################################
# pytest -v --capture=no tests/1_local/test_shell.py
# pytest -v  tests/1_local/test_shell.py
# pytest -v --capture=no  tests/1_local/test_shell..py::Test_name::<METHODNAME>
###############################################################
import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING
import sys

Benchmark.debug()

cloud = locals

shell = Shell()


@pytest.mark.incremental
class TestName:

    def test_terminal_type(self):
        HEADING()
        print(shell.terminal_type())

    def test_run(self):
        HEADING()
        Benchmark.Start()
        r = Shell.run("cms help")
        Benchmark.Stop()
        print(r)
        assert len(r) > 0

    def test_run2(self):
        HEADING()
        Benchmark.Start()
        r = Shell.run("cms help")
        Benchmark.Stop()
        print(r)
        assert len(r) > 0

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag=cloud)
