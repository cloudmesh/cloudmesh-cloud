from cloudmesh.management.configuration.config import Config
from cloudmesh.common.util import HEADING
from pprint import pprint
import textwrap
import oyaml as yaml

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
            name: {cloudmesh.other.name}
          other:
            name: {cloudmesh.profile.name}
        
        """)

        print(spec)
        spec = spec.replace("{", "{{")
        spec = spec.replace("}", "{}")

        data = yaml.load(spec)

        pprint(data)

        for i in range(0, 1):
            spec = spec.format(data)
            pprint(data)

        print(spec)
