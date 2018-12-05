import time
from cm4.vm.Vm import Vm
from cm4.configuration.config import Config
from cm4.common.debug import HEADING, myself

# nosetest -v --nopature
# nosetests -v --nocapture tests/test_mongo.py


class TestMongo:

    def setup(self):
        self.config = Config()

    def test_10_config_print(self):
        print(self.config)
        assert True is True
