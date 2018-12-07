import time
from cm4.vm.Vm import Vm
from cm4.configuration.config import Config
from cm4.mongo.mongoDB import MongoDB
from cm4.common.debug import HEADING, myself
import subprocess

# nosetest -v --nopature
# nosetests -v --nocapture tests/test_vagrant.py


class TestMongo:

    def setup(self):
        pass

    def test_01_vagranttest_status(self):
        HEADING(myself())
        r = subprocess.check_output("cm4 vagrant list", shell=True)
        assert "node1" in r.decode("utf-8")