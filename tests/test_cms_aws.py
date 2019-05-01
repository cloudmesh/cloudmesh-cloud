###############################################################
# pytest -v --capture=no tests/test_cms_aws.py
# pytest -v  tests/test_cms_aws.py
# pytest -v --capture=no -v --nocapture tests/test_cms_aws.py:Test_cms_aws.<METHIDNAME>
###############################################################
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.util import HEADING
from pprint import pprint
import textwrap
import oyaml as yaml
import munch
import re
import time

from cloudmesh.common.Shell import Shell
from cloudmesh.DEBUG import VERBOSE
from cloudmesh.mongo.CmDatabase import CmDatabase
import pytest
from cloudmesh.common.StopWatch import StopWatch

@pytest.mark.incremental
class Test_cms_aws:

    def setup(self):
        conf = Config("~/.cloudmesh/cloudmesh4.yaml")["cloudmesh"]
        cred = conf["cloud"]['aws']["credentials"]
        self.key = (cred['EC2_PRIVATE_KEY_FILE_NAME']).split('.')[0]

    def test_01_boot(self):
        HEADING()

        StopWatch.start("cms vm boot dryrun")
        result = Shell.execute("cms vm boot --name=test_boot_01 --cloud=aws --username=root --image=ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-20190212  --flavor=t2.micro --public --key={} --dryrun".format(self.key), shell=True)
        StopWatch.stop("cms vm boot dryrun")

        VERBOSE(result)

        assert "create nodes ['test_boot_01']" in result
        assert "image - ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-20190212" in result
        assert "flavor - t2.micro" in result
        assert "assign public ip - True" in result
        assert "security groups - None" in result
        assert "keypair name - "+self.key in result

    def test_02_boot(self):
        HEADING()

        StopWatch.start("cms vm boot dryrun")
        result = Shell.execute("cms vm boot --n=2 --cloud=aws --username=root --image=ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-20190212  --flavor=t2.micro --public --key={} --dryrun".format(self.key), shell=True)
        StopWatch.stop("cms vm boot dryrun")

        VERBOSE(result)

        assert "create nodes" in result
        assert "image - ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-20190212" in result
        assert "flavor - t2.micro" in result
        assert "assign public ip - True" in result
        assert "security groups - None" in result
        assert "keypair name - "+self.key in result

    def test_03_boot(self):
        HEADING()

        StopWatch.start("cms vm boot")
        result = Shell.execute("cms vm boot --name=test_boot_01,test_boot_02 --cloud=aws --username=root --image=ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-20190212  --flavor=t2.micro --public --key={}".format(self.key), shell=True)
        StopWatch.stop("cms vm boot")

        VERBOSE(result)

        assert "cm.name" in result
        assert "cm.cloud" in result
        assert "state" in result
        assert "image" in result
        assert "public_ips" in result
        assert "private_ips" in result
        assert "cm.kind" in result

    def test_04_boot(self):
        HEADING()

        StopWatch.start("cms vm boot")
        result = Shell.execute("cms vm boot --n=2 --cloud=aws --username=root --image=ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-20190212  --flavor=t2.micro --public --key={}".format(self.key), shell=True)
        StopWatch.stop("cms vm boot")

        VERBOSE(result)

        assert "cm.name" in result
        assert "cm.cloud" in result
        assert "state" in result
        assert "image" in result
        assert "public_ips" in result
        assert "private_ips" in result
        assert "cm.kind" in result

    def test_list(self):
        HEADING()

        StopWatch.start("cms vm list")
        r1 = Shell.execute("cms vm list test_boot_01 --cloud=aws --output=table --refresh", shell=True)
        r2 = Shell.execute("cms vm list test_boot_01 --cloud=aws --output=table", shell=True)
        StopWatch.stop("cms vm list")

        assert r1==r2

    def test_status(self):
        HEADING("please patiently wait for vm to boot and proceed with other tests")

        # wait for vms to boot for further tests
        while 'pending' in Shell.execute("cms vm list test_boot_01 --refresh", shell=True):
            time.sleep(1)

        StopWatch.start("cms vm status")
        result = Shell.execute("cms vm status test_boot_01 --cloud=aws", shell=True)
        StopWatch.stop("cms vm status")

        VERBOSE(result)

        assert "{'test_boot_01': 'running'}" in result

    def test_01_stop(self):
        HEADING()

        StopWatch.start("cms vm stop dryrun")
        result = Shell.execute("cms vm stop test_boot_02 --cloud=aws --dryrun", shell=True)
        StopWatch.stop("cms vm stop dryrun")

        VERBOSE(result)

        assert "stop nodes ['test_boot_02']" in result
        assert "option - iter" in result
        assert "processors - None" in result

    def test_02_stop(self):
        HEADING()

        StopWatch.start("cms vm stop dryrun")
        result = Shell.execute("cms vm stop test_boot_02 --cloud=aws --parallel --processors=3 --dryrun", shell=True)
        StopWatch.stop("cms vm stop dryrun")

        VERBOSE(result)

        assert "stop nodes ['test_boot_02']" in result
        assert "option - pool" in result
        assert "processors - 3" in result

    def test_03_stop(self):
        HEADING()

        StopWatch.start("cms vm stop")
        result = Shell.execute("cms vm stop test_boot_02 --cloud=aws", shell=True)
        StopWatch.stop("cms vm stop")

        VERBOSE(result)

        assert "test_boot_02" in result

    def test_ping(self):
        HEADING()

        StopWatch.start("cms vm ping")
        result = Shell.execute("cms vm ping test_boot_01 --cloud=aws --count=3 --processors=3", shell=True)
        StopWatch.stop("cms vm ping")

        VERBOSE(result)

        assert "ok" in result
        assert "3 packets transmitted" in result

    def test_check(self):
        HEADING()

        StopWatch.start("cms vm check")
        result = Shell.execute("cms vm check test_boot_01 --cloud=aws --username=ubuntu --processors=3", shell=True)
        StopWatch.stop("cms vm check")

        VERBOSE(result)

        assert "ok" in result

    def test_01_run(self):
        HEADING()

        StopWatch.start("cms vm run dryrun")
        result = Shell.execute("cms vm run --name=test_boot_01 --username=ubuntu --dryrun uname", shell=True)
        StopWatch.stop("cms vm run dryrun")

        VERBOSE(result)

        assert "run command uname on vms: ['test_boot_01']" in result

    def test_02_run(self):
        HEADING()

        StopWatch.start("cms vm run dryrun")
        result = Shell.execute("cms vm run --name=test_boot_01 --username=ubuntu uname", shell=True)
        StopWatch.stop("cms vm run dryrun")

        VERBOSE(result)

        assert "Linux" in result

    def test_01_script(self):
        HEADING()

        StopWatch.start("cms vm script dryrun")
        result = Shell.execute("cms vm script --name=test_boot_01 --username=ubuntu ./test_cms_aws.sh --dryrun", shell=True)
        StopWatch.stop("cms vm script dryrun")

        VERBOSE(result)

        assert "run script ./test_cms_aws.sh on vms: ['test_boot_01']" in result

    def test_02_script(self):
        HEADING()

        StopWatch.start("cms vm script dryrun")
        result = Shell.execute("cms vm script --name=test_boot_01 --username=ubuntu ./test_cms_aws.sh", shell=True)
        StopWatch.stop("cms vm script dryrun")

        VERBOSE(result)

        assert "Linux" in result

    def test_01_start(self):
        HEADING()

        StopWatch.start("cms vm start dryrun")
        result = Shell.execute("cms vm start test_boot_02 --cloud=aws --dryrun", shell=True)
        StopWatch.stop("cms vm start dryrun")

        VERBOSE(result)

        assert "start nodes ['test_boot_02']" in result
        assert "option - iter" in result
        assert "processors - None" in result

    def test_02_start(self):
        HEADING()

        StopWatch.start("cms vm start dryrun")
        result = Shell.execute("cms vm start test_boot_02 --parallel --processors=3 --dryrun", shell=True)
        StopWatch.stop("cms vm start dryrun")

        VERBOSE(result)

        assert "start nodes ['test_boot_02']" in result
        assert "option - pool" in result
        assert "processors - 3" in result

    def test_03_start(self):
        HEADING()

        StopWatch.start("cms vm start")
        result = Shell.execute("cms vm start test_boot_02", shell=True)
        StopWatch.stop("cms vm start")

        VERBOSE(result)

        assert "test_boot_02" in result

    def test_01_terminate(self):
        HEADING()

        StopWatch.start("cms vm delete dryrun")
        result = Shell.execute("cms vm delete test_boot_01 --dryrun", shell=True)
        StopWatch.stop("cms vm delete dryrun")

        VERBOSE(result)

        assert "delete nodes ['test_boot_01']" in result
        assert "option - iter" in result
        assert "processors - None" in result

    def test_02_terminate(self):
        HEADING()

        StopWatch.start("cms vm terminate dryrun")
        result = Shell.execute("cms vm terminate test_boot_01 --parallel --processors=3 --dryrun", shell=True)
        StopWatch.stop("cms vm terminate dryrun")

        VERBOSE(result)

        assert "terminate nodes ['test_boot_01']" in result
        assert "option - pool" in result
        assert "processors - 3" in result

    def test_03_terminate(self):
        HEADING()

        while 'pending' in Shell.execute("cms vm list test_boot_01 --refresh", shell=True):
            time.sleep(1)

        StopWatch.start("cms vm terminate")
        result = Shell.execute("cms vm terminate test_boot_01", shell=True)
        StopWatch.stop("cms vm terminate")

        VERBOSE(result)

        assert "test_boot_01" in result

    def test_01_delete(self):
        HEADING()

        StopWatch.start("cms vm delete dryrun")
        result = Shell.execute("cms vm delete test_boot_02 --dryrun", shell=True)
        StopWatch.stop("cms vm delete dryrun")

        VERBOSE(result)

        assert "delete nodes ['test_boot_02']" in result
        assert "option - iter" in result
        assert "processors - None" in result

    def test_02_delete(self):
        HEADING()

        StopWatch.start("cms vm delete dryrun")
        result = Shell.execute("cms vm delete test_boot_02 --parallel --processors=3 --dryrun", shell=True)
        StopWatch.stop("cms vm delete dryrun")

        VERBOSE(result)

        assert "delete nodes ['test_boot_02']" in result
        assert "option - pool" in result
        assert "processors - 3" in result

    def test_03_delete(self):
        HEADING()

        while 'pending' in Shell.execute("cms vm list test_boot_02 --refresh", shell=True):
            time.sleep(1)

        StopWatch.start("cms vm delete")
        result = Shell.execute("cms vm delete test_boot_02", shell=True)
        StopWatch.stop("cms vm delete")

        VERBOSE(result)

        assert "test_boot_02" in result
