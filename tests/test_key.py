###############################################################
# pytest -v --capture=no tests/test_key.py
# pytest -v  tests/test_key.py
# pytest -v --capture=no  tests/test_key.py:Test_key.<METHIDNAME>
###############################################################
from pprint import pprint
from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import HEADING
from cloudmesh.management.configuration.SSHkey import SSHkey
from cloudmesh.management.configuration.config import Config
import pytest


@pytest.mark.incremental
class TestName:

    def setup(self):
        self.sshkey = SSHkey()

    def test_key(self):
        HEADING()
        pprint(self.sshkey)
        print(self.sshkey)
        print(type(self.sshkey))
        pprint(self.sshkey.__dict__)

        assert self.sshkey.__dict__ is not None

    def test_git(self):
        HEADING()
        config = Config()
        username = config["cloudmesh.profile.github"]
        print("Username:", username)
        keys = self.sshkey.get_from_git(username)
        pprint(keys)
        print(Printer.flatwrite(keys,
                                sort_keys=["name"],
                                order=["name", "fingerprint"],
                                header=["Name", "Fingerprint"])
              )

        assert len(keys) > 0
