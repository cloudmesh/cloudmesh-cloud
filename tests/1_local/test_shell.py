###############################################################
# pytest -v --capture=no tests/1_local/test_shell.py
# pytest -v  tests/1_local/test_shell.py
# pytest -v --capture=no  tests/1_local/test_shell.py:Test_name.<METHIDNAME>
###############################################################
import warnings
warnings.simplefilter("once")

import pytest
from cloudmesh.common3.Benchmark import Benchmark
from cloudmesh.common3.Shell import Shell
from cloudmesh.common.util import HEADING

Benchmark.debug()

shell = Shell()


@pytest.mark.incremental
class TestName:

    def test_shell(self):
        HEADING()
        Benchmark.Start()
        shell = Shell()
        Benchmark.Stop()

        print(shell.terminal_type())

    def test_pwd(self):
        HEADING()
        Benchmark.Start()
        r = shell.execute('pwd')
        Benchmark.Stop()
        print(r)

    def test_ls_la_list(self):
        HEADING()
        Benchmark.Start()
        r = shell.execute('ls', ["-l", "-a"])
        Benchmark.Stop()
        print(r)

    def test_ls_la_string(self):
        HEADING()
        Benchmark.Start()
        r = shell.execute('ls', "-l -a")
        Benchmark.Stop()
        print(r)

    def test_ls_la_wrapper(self):
        HEADING()
        Benchmark.Start()
        r = shell.ls("-la")
        Benchmark.Stop()
        print(r)

    def test_ls_la_wrapper_multi_options(self):
        HEADING()
        Benchmark.Start()
        r = shell.ls("-a", "-l")
        Benchmark.Stop()
        print(r)

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True)
