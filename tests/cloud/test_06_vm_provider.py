###############################################################
# pytest -v --capture=no tests/cloud/test_provider_vm06_vm_provider.py
# pytest -v  tests/cloud/test_provider_vm06_vm_provider.py
###############################################################

# TODO: start this with cloud init, e.g, empty mongodb
# TODO: assertuons need to be added

import pytest
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables
from cloudmesh.common3.Benchmark import Benchmark
from cloudmesh.compute.vm.Provider import Provider
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


name_generator = Name(schema=f"test-{user}-vm-""{counter}", counter=1)
name_generator.incr()
name = str(name_generator)

provider = Provider(name=cloud)


def Print(data):
    print(provider.Print(data=data, output='table', kind='vm'))

current_vms = 0

@pytest.mark.incremental
class Test_provider_vm:

    def test_provider_vmprovider_vm_list(self):
        HEADING()
        Benchmark.Start()
        data = provider.list()
        current_vms = len(data)
        Benchmark.Stop()
        Print(data)


    def test_provider_vm_create(self):
        HEADING()
        Benchmark.Start()
        data = provider.create()
        Benchmark.Stop()
        print(data)

    def test_provider_vm_stop(self):
        HEADING()
        Benchmark.Start()
        data = provider.stop(name=name)
        Benchmark.Stop()
        print(data)

        # check the status of the vm if it is stopped

    def test_provider_vm_start(self):
        HEADING()
        Benchmark.Start()
        data = provider.start(name=name)
        Benchmark.Stop()
        print(data)

        # check the status of the vm if it is started

    def test_provider_vm_status(self):
        HEADING()
        Benchmark.Start()
        data = provider.status(name=name)
        Benchmark.Stop()
        print(data)

    def test_provider_vm_info(self):
        HEADING()
        Benchmark.Start()
        data = provider.info(name=name)
        Benchmark.Stop()
        print(data)

    # do other tests before terminationg, keys, metadata, ....

    def test_provider_vm_terminate(self):
        HEADING()
        Benchmark.Start()
        data = provider.terminate(name=name)
        Benchmark.Stop()
        print(data)

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=False, tag=cloud)
