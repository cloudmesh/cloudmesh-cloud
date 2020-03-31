###############################################################
# pip install .; pytest -v --capture=no  tests/aws/test_aws..py::Test_aws.test_001
# pytest -v --capture=no tests/aws/test_aws.py
# pytest -v  tests/aws/test_aws.py
###############################################################

import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
from cloudmesh.compute.aws.Provider import Provider
from cloudmesh.management.configuration.name import Name

Benchmark.debug()

#
# TODO: THIS IS A BUG, the deprecated api shoudl not be used
#

CLOUD = "aws"


@pytest.mark.incremental
class Test_Vafa:
    def test_aws_aws_list(self):
        HEADING()
        provider = Provider(name=CLOUD)
        print(provider.list())

    def test_aws_aws_boot(self):
        HEADING()
        name = Name()
        name.incr()
        vm_name = str(name)
        provider = Provider(name=CLOUD)
        vm = provider.create(name=vm_name, image="ami-0c929bde1796e1484",
                             size="t2.micro")
        print(vm)
        print(provider.list())

    def test_benchmark(self):
        Benchmark.print(csv=True, sysinfo=False, tag=CLOUD)
