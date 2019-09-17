###############################################################
# pytest -v --capture=no tests/cloud/test_06_vm_provider.py
# pytest -v  tests/cloud/test_06_vm_provider.py
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

import sys

Benchmark.debug()

user = Config()["cloudmesh.profile.user"]
variables = Variables()
VERBOSE(variables.dict())

key = variables['key']

cloud = variables.parameter('cloud')

print(f"Test run for {cloud}")

if cloud is None:
    raise ValueError("cloud is not not set")


name_generator = Name()
name_generator.set(f"test-{user}-vm-" + "{counter}")


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
        name_generator.incr()
        Benchmark.Start()
        data = provider.create(key=key)
        Benchmark.Stop()
        # print(data)
        VERBOSE(data)
        name = str(Name())
        status = provider.status(name=name)[0]
        assert status["cm.status"] in ['ACTIVE', 'BOOTING']

    def test_provider_vm_info(self):
        HEADING()
        Benchmark.Start()
        data = provider.info(name=name)[0]
        Benchmark.Stop()
        print(data)
        assert data["cm"]["status"] in ['ACTIVE', 'BOOTING']

    def test_vm_status(self):
        HEADING()
        name = str(Name())
        Benchmark.Start()
        data = provider.status(name=name)[0]
        Benchmark.Stop()
        assert data["cm.status"] in ['ACTIVE', 'BOOTING']

    def test_provider_vm_start(self):
        HEADING()
        name = str(Name())
        Benchmark.Start()
        data = provider.start(name=name)
        Benchmark.Stop()
        VERBOSE(data)
        status = provider.status(name=name)[0]
        assert status["cm.status"] in ['ACTIVE', 'BOOTING']

    def test_provider_vm_stop(self):
        HEADING()
        name = str(Name())
        Benchmark.Start()
        data = provider.stop(name=name)
        Benchmark.Stop()
        VERBOSE(data)
        status = provider.status(name=name)[0]
        assert status["cm.status"] in ['ACTIVE', 'BOOTING', 'STOPPED']

    # do other tests before terminationg, keys, metadata, ....

    def test_provider_vm_terminate(self):
        HEADING()
        name = str(Name())
        Benchmark.Start()
        data = provider.destroy(name=name)
        Benchmark.Stop()
        print(data)
        data = provider.info(name=name)
        #below cm.status check required as in aws it takes a while to clear list from you account after terminating vm
        assert len(data) == 0 or ( data[0]["cm"]["status"] in ['BOOTING','TERMINATED'] if data and data[0].get('cm',None) is not None else True)


    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)
