import time
#from cm4.vm.Vm import Vm
from cm4.configuration.config import Config
# from cm4.mongo.mongoDB import MongoDB
from cm4.common.debug import HEADING, myself
import subprocess

# nosetest -v --nopature
# nosetests -v --nocapture tests/test_vbox.py


class Test_vagrant:

    def setup(self):
        pass

    def rprint(self, r):
        print (". Begin .", 70 * ".")
        print (r)
        print (". End   .", 70 * ".")


    def test_01_image_add(self):
        HEADING(myself())
        r = subprocess.check_output("cms vbox image add ubuntu/bionic64", shell=True).decode("utf-8")

        self.rprint(r)

        assert "ubuntu/bionic64" in r

    def test_02_image_list(self):
        HEADING(myself())
        r = subprocess.check_output("cms vbox image list", shell=True).decode("utf-8")
        self.rprint (r)

        assert "ubuntu/bionic64" in r


    def test_03_image_boot(self):
        HEADING(myself())
        r = subprocess.check_output("cms vbox vm create test-bionic", shell=True).decode("utf-8")
        self.rprint (r)
        assert "ubuntu/bionic64" in r

        r = subprocess.check_output("cms vbox vm boot test-bionic", shell=True).decode("utf-8")
        self.rprint (r)
        assert "ubuntu/bionic64" in r
