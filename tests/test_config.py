from cloudmesh.management.configuration.config import Config
from cloudmesh.management.debug import myself, HEADING
from pprint import pprint


# nosetests -v --nocapture tests/test_config.py


class TestConfig:

    def setup(self):
        self.config = Config()

    def test_00_config(self):
        HEADING(myself())

        pprint(self.config.dict())

        print(self.config)
        print(type(self.config.data))

        assert self.config is not None


    def test_20_config_subscriptable(self):
        HEADING(myself())
        data = self.config["cloudmesh"]["data"]["mongo"]
        assert data is not None
