###############################################################
# pytest -v --capture=no tests/cloud/test_secgroup_prvider.py
# pytest -v  tests/cloud/test_secgroup_prvider.py
###############################################################

# TODO: start this with cloud init, e.g, empty mongodb
# TODO: assertuons need to be added

import pytest
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables
from cloudmesh.common3.Benchmark import Benchmark
from cloudmesh.compute.openstack.Provider import Provider
from cloudmesh.configuration.Config import Config
from cloudmesh.management.configuration.name import Name


Benchmark.debug()

user = Config()["cloudmesh.profile.user"]
variables = Variables()
VERBOSE(variables.dict())

cloud = variables.parameter('cloud')

print(f"Test run for {cloud}")

if cloud is None:
    raise ValueError("cloud is not not set")


name_generator = Name(schema=f"test-{user}-vm", counter=1)

provider = Provider(name=cloud)



@pytest.mark.incremental
class Test_provider:

    def test_list(self):
        HEADING()
        Benchmark.Start()
        data = provider.list()
        Benchmark.Stop()
        print(data)

    def test_create(self):
        HEADING()
        Benchmark.Start()
        data = provider.create()
        Benchmark.Stop()
        print(data)
        self.name = data['name']

    def test_stop(self):
        HEADING()
        Benchmark.Start()
        data = provider.stop(name=self.name)
        Benchmark.Stop()
        print(data)

        # check the status of the vm if it is stopped

    def test_start(self):
        HEADING()
        Benchmark.Start()
        data = provider.start(name=self.name)
        Benchmark.Stop()
        print(data)

        # check the status of the vm if it is started

    def test_status(self):
        HEADING()
        Benchmark.Start()
        data = provider.status(name=self.name)
        Benchmark.Stop()
        print(data)

    def test_info(self):
        HEADING()
        Benchmark.Start()
        data = provider.info(name=self.name)
        Benchmark.Stop()
        print(data)

    # do uther tests befor terminationg, keys, metadata, ....

    def test_terminate(self):
        HEADING()
        Benchmark.Start()
        data = provider.terminate(name=self.name)
        Benchmark.Stop()
        print(data)

    def test_benchmark(self):
        Benchmark.print()
