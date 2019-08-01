###############################################################
# pytest -v --capture=no tests/1_local/test_shell.py
# pytest -v  tests/1_local/test_shell.py
# pytest -v --capture=no  tests/1_local/test_shell.py:Test_name.<METHIDNAME>
###############################################################
import pytest
from cloudmesh.common3.Benchmark import Benchmark
from cloudmesh.common3.Shell import Shell

Benchmark.debug()

shell = Shell()


@pytest.mark.incremental
class TestName:

    def test_shell(self):
        Benchmark.Start()
        shell = Shell()
        Benchmark.Stop()

        print(shell.terminal_type())

    def test_pwd(self):
        Benchmark.Start()
        r = shell.execute('pwd')
        Benchmark.Stop()
        print(r)

    def test_ls_la_list(self):
        Benchmark.Start()
        r = shell.execute('ls', ["-l", "-a"])
        Benchmark.Stop()
        print(r)

    def test_ls_la_string(self):
        Benchmark.Start()
        r = shell.execute('ls', "-l -a")
        Benchmark.Stop()
        print(r)

    def test_ls_la_wrapper(self):
        Benchmark.Start()
        r = shell.ls("-la")
        Benchmark.Stop()
        print(r)

    def test_ls_la_wrapper_multi_options(self):
        Benchmark.Start()
        r = shell.ls("-a", "-l")
        Benchmark.Stop()
        print(r)

    def test_benchmark(self):
        Benchmark.print()
