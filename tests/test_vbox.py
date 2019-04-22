###############################################################
# pytest -v --capture=no tests/test_vbox.py
# pytest -v  tests/test_vbox.py
# pytest -v --capture=no  tests/test_vbox.py:Test_vbox.<METHIDNAME>
###############################################################
# from cloud.vm.Vm import Vm
# from cloud.mongo.mongoDB import MongoDB
from cloudmesh.management.debug import HEADING, myself
import subprocess
import pytest


@pytest.mark.incremental
class Test_vagrant:

    def setup(self):
        pass

    def rprint(self, r):
        print(". Begin .", 70 * ".")
        print(r)
        print(". End   .", 70 * ".")

    def test_version(self):
        cmd = "cms vbox version"
        result = subprocess.check_output(cmd, shell=True).decode("utf-8")
        assert "Vagrant Version" in result

    def test_image_add(self):
        HEADING(myself())
        r = subprocess.check_output("cms vbox image add ubuntu/bionic64", shell=True).decode("utf-8")

        self.rprint(r)

        assert "ubuntu/bionic64" in r

    def test_image_list(self):
        HEADING(myself())
        r = subprocess.check_output("cms vbox image list", shell=True).decode("utf-8")
        self.rprint(r)

        assert "ubuntu/bionic64" in r

    def test_image_boot(self):
        HEADING(myself())
        r = subprocess.check_output("cms vbox vm create test-bionic", shell=True).decode("utf-8")
        self.rprint(r)
        assert "ubuntu/bionic64" in r

        r = subprocess.check_output("cms vbox vm boot test-bionic", shell=True).decode("utf-8")
        self.rprint(r)
        assert "ubuntu/bionic64" in r
