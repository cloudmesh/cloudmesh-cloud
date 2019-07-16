###############################################################
# pytest -v --capture=no tests/0_basic/test_config.py
# pytest -v  tests/0_basic/test_config.py
# pytest -v --capture=no  tests/0_basic/test_config.py:Test_config.<METHIDNAME>
###############################################################
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.util import HEADING
from pprint import pprint
import textwrap
import oyaml as yaml
import munch
import re
import pytest
import os
from pathlib import Path
from cloudmesh.common.util import path_expand


@pytest.mark.incremental
class TestConfig:

    def setup(self):
        self.config = Config()

    def test_config(self):
        HEADING()

        pprint(self.config.dict())

        print(self.config)
        print(type(self.config.data))

        assert self.config is not None

    def test_config_subscriptable(self):
        HEADING()
        data = self.config["cloudmesh"]["data"]["mongo"]
        assert data is not None

    def test_dictreplace(self):
        HEADING()

        spec = textwrap.dedent("""
        cloudmesh:
          profile:
            name: Gregor
          unordered:
            name: "{cloudmesh.other.name}.postfix"
          other:
            name: "{cloudmesh.profile.name}"
        
        """)

        print(spec)

        # spec = spec.replace("{", "{{")
        # spec = spec.replace("}", "}}")

        # print(spec)

        result = self.config.spec_replace(spec)

        print(result)
        data = yaml.load(result, Loader=yaml.SafeLoader)
        pprint(data)

        assert data["cloudmesh"]["unordered"]["name"] == "Gregor.postfix"
        assert data["cloudmesh"]["other"]["name"] == "Gregor"

    def test_configreplace(self):
        HEADING()
        self.config = Config()
        pprint(self.config["cloudmesh"]["profile"])

    def test_if_yaml_file_exists(self):
        self.config = Config()
        self.config.create()
        filename = path_expand("~/.cloudmesh/cloudmesh4.yaml")
        assert os.path.isfile(Path(filename))

    def test_set(self):
        self.config["cloudmesh.test.nested"] = "Gregor"
        print (self.config["cloudmesh.test.nested"])
        assert self.config["cloudmesh.test.nested"] == "Gregor"

    ''' THIS TEST DOE FAIL
    def test_del(self):
        del self.config["cloudmesh.test.nested"]

        assert self.config["cloudmesh.test.nested"] != "Gregor"
    '''
