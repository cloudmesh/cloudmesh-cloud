###############################################################
# pytest -v --capture=no tests/aws/test_cms_aws.py
# pytest -v  tests/aws/test_cms_aws.py
# pytest -v --capture=no -v --nocapture  tests/aws/test_cms_aws..py::Test_cms_aws::<METHODNAME>
###############################################################
import time

import pytest
from cloudmesh.common.Shell import Shell
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.configuration.Config import Config

Benchmark.debug()

IMAGE = "ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-20190212"
CLOUD = "aws"


@pytest.mark.incremental
class TestCmsAWS:

    def setup(self):
        conf = Config("~/.cloudmesh/cloudmesh.yaml")["cloudmesh"]
        cred = conf["cloud"][CLOUD]["credentials"]
        self.key = (cred['EC2_PRIVATE_KEY_FILE_NAME']).split('.')[0]

    def test_01_boot(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute(
            f"cms vm boot --name=test_boot_01 --cloud={CLOUD} --username=root"
            f" --image={IMAGE}"
            f" --flavor=t2.micro"
            f" --public --key={self.key} --dryrun", shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "create nodes ['test_boot_01']" in result
        assert f"image - {IMAGE}" in result
        assert "flavor - t2.micro" in result
        assert "assign public ip - True" in result
        assert "security groups - None" in result
        assert "keypair name - " + self.key in result

    def test_02_boot(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute(
            f"cms vm boot --n=2 --cloud={CLOUD} --username=root"
            f" --image={IMAGE}"
            f" --flavor=t2.micro --public --key={self.key} --dryrun",
            shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "create nodes" in result
        assert f"image - {IMAGE}" in result
        assert "flavor - t2.micro" in result
        assert "assign public ip - True" in result
        assert "security groups - None" in result
        assert f"keypair name - {self.key}" in result

    def test_03_boot(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute(
            f"cms vm boot --name=test_boot_01,test_boot_02 --cloud={CLOUD}"
            f" --username=root"
            f" --image={IMAGE}"
            f" --flavor=t2.micro --public --key={self.key}",
            shell=True)
        Benchmark.Stop()

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

        Benchmark.Start()
        result = Shell.execute(
            f"cms vm boot --n=2 --cloud={CLOUD} --username=root "
            f" --image={IMAGE}"
            f" --flavor=t2.micro --public --key={self.key}",
            shell=True)
        Benchmark.Stop()

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

        Benchmark.Start()
        r1 = Shell.execute(
            f"cms vm list test_boot_01 --cloud={CLOUD} --output=table --refresh",
            shell=True)
        r2 = Shell.execute(
            f"cms vm list test_boot_01 --cloud={CLOUD} --output=table",
            shell=True)
        Benchmark.Stop()

        assert r1 == r2

    def test_status(self):
        HEADING(
            "please patiently wait for vm to boot and proceed with other tests")

        # wait for vms to boot for further tests
        while 'pending' in Shell.execute("cms vm list test_boot_01 --refresh",
                                         shell=True):
            time.sleep(1)

        Benchmark.Start()
        result = Shell.execute(f"cms vm status test_boot_01 --cloud={CLOUD}",
                               shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "{'test_boot_01': 'running'}" in result

    def test_01_stop(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute(
            f"cms vm stop test_boot_02 --cloud={CLOUD} --dryrun",
            shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "stop nodes ['test_boot_02']" in result
        assert "option - iter" in result
        assert "processors - None" in result

    def test_02_stop(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute(
            f"cms vm stop test_boot_02 --cloud={CLOUD} --parallel --processors=3 --dryrun",
            shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "stop nodes ['test_boot_02']" in result
        assert "option - pool" in result
        assert "processors - 3" in result

    def test_03_stop(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute(f"cms vm stop test_boot_02 --cloud={CLOUD}",
                               shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "test_boot_02" in result

    def test_ping(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute(
            f"cms vm ping test_boot_01 --cloud={CLOUD} --count=3 --processors=3",
            shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "ok" in result
        assert "3 packets transmitted" in result

    def test_check(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute(
            f"cms vm check test_boot_01 --cloud={CLOUD} --username=ubuntu --processors=3",
            shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "ok" in result

    def test_01_run(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute(
            "cms vm run --name=test_boot_01 --username=ubuntu --dryrun uname",
            shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "run command uname on vms: ['test_boot_01']" in result

    # def test_02_run(self):
    #     HEADING()
    #
    #     Benchmark.Start()
    #     result = Shell.execute("cms vm run --name=test_boot_01 --username=ubuntu uname", shell=True)
    #     Benchmark.Stop()
    #
    #     VERBOSE(result)
    #
    #     assert "Linux" in result

    def test_01_script(self):
        HEADING()

        Benchmark.Start()
        #
        # TODO: location is a bug as we can not assum test is run in .
        # alos the sh command has been removed and should be created in this
        # test
        #
        result = Shell.execute(
            "cms vm script --name=test_boot_01 --username=ubuntu ./test_cms_aws.sh --dryrun",
            shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "run script ./test_cms_aws.sh on vms: ['test_boot_01']" in result

    # def test_02_script(self):
    #     HEADING()
    #
    #     Benchmark.Start()
    #     result = Shell.execute("cms vm script --name=test_boot_01 --username=ubuntu ./test_cms_aws.sh", shell=True)
    #     Benchmark.Stop()
    #
    #     VERBOSE(result)
    #
    #     assert "Linux" in result

    def test_01_start(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute(
            f"cms vm start test_boot_02 --cloud={CLOUD} --dryrun",
            shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "start nodes ['test_boot_02']" in result
        assert "option - iter" in result
        assert "processors - None" in result

    def test_02_start(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute(
            "cms vm start test_boot_02 --parallel --processors=3 --dryrun",
            shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "start nodes ['test_boot_02']" in result
        assert "option - pool" in result
        assert "processors - 3" in result

    def test_03_start(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms vm start test_boot_02", shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "test_boot_02" in result

    def test_01_terminate(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms vm delete test_boot_01 --dryrun",
                               shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "delete nodes ['test_boot_01']" in result
        assert "option - iter" in result
        assert "processors - None" in result

    def test_02_terminate(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute(
            "cms vm terminate test_boot_01 --parallel --processors=3 --dryrun",
            shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "terminate nodes ['test_boot_01']" in result
        assert "option - pool" in result
        assert "processors - 3" in result

    def test_03_terminate(self):
        HEADING()

        while 'pending' in Shell.execute("cms vm list test_boot_01 --refresh",
                                         shell=True):
            time.sleep(1)

        Benchmark.Start()
        result = Shell.execute("cms vm terminate test_boot_01", shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "test_boot_01" in result

    def test_01_delete(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms vm delete test_boot_02 --dryrun",
                               shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "delete nodes ['test_boot_02']" in result
        assert "option - iter" in result
        assert "processors - None" in result

    def test_02_delete(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute(
            "cms vm delete test_boot_02 --parallel --processors=3 --dryrun",
            shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "delete nodes ['test_boot_02']" in result
        assert "option - pool" in result
        assert "processors - 3" in result

    def test_03_delete(self):
        HEADING()

        while 'pending' in Shell.execute("cms vm list test_boot_02 --refresh",
                                         shell=True):
            time.sleep(1)

        Benchmark.Start()
        result = Shell.execute("cms vm delete test_boot_02", shell=True)
        Benchmark.Stop()

        VERBOSE(result)

        assert "test_boot_02" in result

    def test_benchmark(self):
        Benchmark.print(csv=True, sysinfo=False, tag=CLOUD)

