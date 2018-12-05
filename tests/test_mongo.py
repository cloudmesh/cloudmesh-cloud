import time
from cm4.vm.Vm import Vm
from cm4.configuration.config import Config
from cm4.common.debug import HEADING, myself

# nosetest -v --nopature
# nosetests -v --nocapture tests/test_mongo.py

class TestCloudAzure:

    def setup(self):
        self.config = Config()

    def test_01_config(self):
        print(self.config)
        assert True