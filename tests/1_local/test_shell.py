###############################################################
# pytest -v --capture=no tests/1_local/test_shell.py
# pytest -v  tests/1_local/test_shell.py
# pytest -v --capture=no  tests/1_local/test_shell.py:Test_name.<METHODNAME>
###############################################################
import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING

Benchmark.debug()

shell = Shell()


@pytest.mark.incremental
class TestName:

    def test_terminal_type(self):
        HEADING()
        print(shell.terminal_type())

    def test_pwd(self):
        HEADING()
        Benchmark.Start()
        r = Shell.execute('pwd')
        Benchmark.Stop()
        print(r)

    def test_ls_la_list(self):
        HEADING()
        Benchmark.Start()
        r = Shell.execute('ls', ["-l", "-a"])
        Benchmark.Stop()
        print(r)

    def test_ls_la_string(self):
        HEADING()
        Benchmark.Start()
        r = Shell.execute('ls', "-l -a")
        Benchmark.Stop()
        print(r)

    def test_ls(self):
        HEADING()
        Benchmark.Start()
        r = Shell.ls(".", "*")
        Benchmark.Stop()
        print(r)

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True)
