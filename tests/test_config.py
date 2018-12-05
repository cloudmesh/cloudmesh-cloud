from cm4.configuration.config import Config
from cm4.common.debug import myself, HEADING
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
        #pprint(config.credentials('local'))

        assert self.config is not None
        #assert 'cloud' in config.cloud

    def test_10_config_print(self):
        print(self.config)
        assert True is True

    def test_20_config_subscriptable(self):
        data = self.config["cloudmesh"]["data"]["mongo"]
        assert data is not None
