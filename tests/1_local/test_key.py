###############################################################
# pytest -v --capture=no tests/1_local/test_key.py
# pytest -v  tests/1_local/test_key.py
# pytest -v --capture=no  tests/1_local/test_key.py:Test_key.<METHIDNAME>
###############################################################
from pprint import pprint

import pytest
from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import HEADING
from cloudmesh.common3.Benchmark import Benchmark
from cloudmesh.management.configuration.SSHkey import SSHkey
from cloudmesh.configuration.Config import Config


@pytest.mark.incremental
class TestName:

    def test_key(self):
        HEADING()

        Benchmark.Start()
        key = SSHkey()
        Benchmark.Stop()

        pprint(key)
        print(key)
        print(type(key))
        pprint(key.__dict__)

        assert key.__dict__ is not None

    def test_git(self):
        HEADING()
        config = Config()
        username = config["cloudmesh.profile.github"]
        print("Username:", username)

        key = SSHkey()
        Benchmark.Start()
        keys = key.get_from_git(username)
        Benchmark.Stop()
        pprint(keys)
        print(Printer.flatwrite(keys,
                                sort_keys=["name"],
                                order=["name", "fingerprint"],
                                header=["Name", "Fingerprint"])
              )

        assert len(keys) > 0

    def test_benchmark(self):
        Benchmark.print()
