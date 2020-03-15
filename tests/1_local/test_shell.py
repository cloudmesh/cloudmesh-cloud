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

    def test_pwd(self):
        HEADING()
        Benchmark.Start()
        r = Shell.execute('pwd')
        Benchmark.Stop()
        print(r)

    def test_execute_list(self):
        if sys.platform != 'win32':
            HEADING()
            Benchmark.Start()
            r = Shell.execute('ls', ["-l", "-a"])
            Benchmark.Stop()
            print(r)
        else:
            HEADING()
            Benchmark.Start()
            r = Shell.execute('whoami', ["/user", "/fo", "table"])
            Benchmark.Stop()
            print(r)

    def test_execute_string(self):
        if sys.platform != 'win32':
            HEADING()
            Benchmark.Start()
            r = Shell.execute('ls', "-l -a")
            Benchmark.Stop()
            print(r)
        else:
            HEADING()
            Benchmark.Start()
            r = Shell.execute('whoami', "/user /fo table")
            Benchmark.Stop()
            print(r)

    def test_ls(self):
        HEADING()
        Benchmark.Start()
        r = Shell.ls("./*.py")
        Benchmark.Stop()
        print(r)
        assert len(r) > 0

    def test_check(self):
        HEADING()
        Benchmark.Start()
        r = Shell.run("cms check")
        Benchmark.Stop()
        print(r)
        assert len(r) > 0

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag=cloud)
