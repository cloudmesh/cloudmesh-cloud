from cloudmesh.management.configuration.config import Config
from cloudmesh.common.util import HEADING
from pprint import pprint
import textwrap
import oyaml as yaml
import munch
import re

# nosetests -v --nocapture tests/test_config.py


class TestConfig:

    def setup(self):
        self.config = Config()

    def test_00_config(self):
        HEADING()

        pprint(self.config.dict())

        print(self.config)
        print(type(self.config.data))

        assert self.config is not None


    def test_20_config_subscriptable(self):
        HEADING()
        data = self.config["cloudmesh"]["data"]["mongo"]
        assert data is not None

    def test_30_dictreplace(self):
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
        data = yaml.load(result)
        pprint(data)

        assert data["cloudmesh"]["unordered"]["name"] == "Gregor.postfix"
        assert data["cloudmesh"]["other"]["name"] == "Gregor"

    def test_31_configreplace(self):
        HEADING()
        self.config = Config()
        pprint(self.config["cloudmesh"]["profile"])
