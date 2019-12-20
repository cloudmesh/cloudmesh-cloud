###############################################################
# pytest -v --capture=no tests/cloud/test_08_vm_provider.py
# pytest -v  tests/cloud/test_08_vm_provider.py
# pytest -v --capture=no  tests/cloud/test_08_vm_provider.py:Test_provider_vm.METHODNAME
###############################################################

# TODO: start this with cloud init, e.g, empty mongodb
# TODO: assertuons need to be added
from pprint import pprint

import pytest
import os
from time import sleep
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.configuration.Config import Config
from cloudmesh.management.configuration.name import Name
from cloudmesh.mongo.CmDatabase import CmDatabase
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

    def test_key_upload(self):
        os.system("cms key add")
        os.system("cms key list")
        os.system(f"cms key upload {key} --cloud={cloud}")
        os.system(f"cms key list --cloud={cloud}")

    def find_counter(self):
        name = str(Name())
        print(name)
        vms = provider.list()
        if vms is not None:
            numbers = []
            names = []
            for vm in vms:
                names.append(vm['name'])
                numbers.append(int(vm['name'].rsplit("-", 1)[1]))
            numbers.sort()
            return numbers[-1]

    def test_find_largest_id(self):
        name = Name()
        counter = {"counter": self.find_counter()}
        name.assign(counter)

    def test_provider_vm_create(self):
        HEADING()
        os.system(f"cms vm list --cloud={cloud}")
        name_generator.incr()
        Benchmark.Start()
        data = provider.create(key=key)
        Benchmark.Stop()
        # print(data)
        VERBOSE(data)
        name = str(Name())
        status = provider.status(name=name)[0]
        print(f'status: {str(status)}')
        if cloud == 'oracle':
            assert status["cm.status"] in ['STARTING', 'RUNNING', 'STOPPING',
                                           'STOPPED']
        else:
            assert status["cm.status"] in ['ACTIVE', 'BOOTING', 'TERMINATED',
                                           'STOPPED']

    def test_provider_vmprovider_vm_list(self):
        # list should be after create() since it would return empty and
        # len(data) would be 0
        HEADING()
        Benchmark.Start()
        data = provider.list()
        assert len(data) > 0
        Benchmark.Stop()
        Print(data)

    def test_provider_vm_wait(self):
        HEADING()
        name = str(Name())
        Benchmark.Start()
        cm = CmDatabase()
        vm = cm.find_name(name, kind="vm")[0]
        assert provider.wait(vm=vm), "cms wait timed out ..."
        Benchmark.Stop()

    def test_provider_vm_ssh(self):
        HEADING()
        name = str(Name())
        Benchmark.Start()
        cm = CmDatabase()
        vm = cm.find_name(name, kind="vm")[0]
        data = provider.ssh(vm=vm, command='\"echo IAmAlive\"')
        print(data)
        assert 'IAmAlive' in data
        Benchmark.Stop()
        VERBOSE(data)

    def test_provider_vm_info(self):
        # This is just a dry run, status test actually uses info() in all
        # provider
        HEADING()
        Benchmark.Start()
        name = str(Name())
        data = provider.info(name=name)
        print("dry run info():")
        pprint(data)
        Benchmark.Stop()

    def test_vm_status(self):
        HEADING()
        name = str(Name())
        Benchmark.Start()
        data = provider.status(name=name)
        if type(data) == list:
            data = data[0]
        print(data)
        Benchmark.Stop()
        if cloud == 'oracle':
            assert data["cm.status"] in ['STARTING', 'RUNNING', 'STOPPING',
                                         'STOPPED']
        else:
            assert data["cm.status"] in ['ACTIVE', 'BOOTING', 'TERMINATED',
                                         'STOPPED']

    def test_provider_vm_stop(self):
        HEADING()
        name = str(Name())
        Benchmark.Start()
        data = provider.stop(name=name)
        Benchmark.Stop()
        stop_timeout = 360
        time = 0
        while time <= stop_timeout:
            sleep(5)
            time += 5
            status = provider.status(name=name)[0]
            if status["cm.status"] in ['STOPPED', 'SHUTOFF']:
                break
        VERBOSE(data)
        print(status)
        assert status["cm.status"] in ['STOPPED', 'SHUTOFF']

    def test_provider_vm_start(self):
        HEADING()
        name = str(Name())
        Benchmark.Start()
        data = provider.start(name=name)
        Benchmark.Stop()
        start_timeout = 360
        time = 0
        while time <= start_timeout:
            sleep(5)
            time += 5
            status = provider.status(name=name)[0]
            # print(f'status {str(status)}')
            if status["cm.status"] in ['ACTIVE', 'BOOTING', 'RUNNING']:
                break
        VERBOSE(data)
        print(status)
        assert status["cm.status"] in ['ACTIVE', 'BOOTING', 'RUNNING']

    # do other tests before terminationg, keys, metadata, .... =>
    # keys is already implemented in test02

    def test_provider_vm_terminate(self):
        HEADING()
        name = str(Name())
        Benchmark.Start()
        data = provider.destroy(name=name)
        Benchmark.Stop()

        pprint(data)

        termination_timeout = 360
        time = 0
        while time <= termination_timeout:
            sleep(5)
            time += 5
            if cloud == 'chameleon' and len(provider.info(name=name)) == 0:
                break
            elif cloud == 'aws' and (len(provider.info(name=name)) == 0 or
                                     provider.info(name=name)[0]["cm"][
                                         "status"] in ['TERMINATED']):
                break
            elif cloud == 'azure':
                try:
                    provider.info(name=name)
                except Exception:
                    # if there is an exception that means the group has been
                    # deleted
                    break

        # print(provider.info(name=name))
        if cloud == 'chameleon':
            assert len(provider.info(name=name)) == 0
        elif cloud == 'aws':
            assert len(data) == 0 if data else True \
                   or (data[0]["cm"]["status"] in ['BOOTING', 'TERMINATED']
                       if data and data[0].get('cm', None) is not None
                       else True)
        elif cloud == 'azure':
            try:
                provider.info(name=name)
            except Exception:
                # if there is an exception that means the group has been
                # deleted
                pass
        elif cloud == 'oracle':
            info = provider.info(name)
            assert info is None or info[0]['_lifecycle_state'] in ['TERMINATED']
        else:
            raise NotImplementedError
        # data = provider.info(name=name)
        # below cm.status check required as in aws it takes a while to clear
        # list from you account after terminating vm
        # assert len(data) == 0 or ( data[0]["cm"]["status"] in
        # ['BOOTING','TERMINATED'] if data and data[0].get('cm',None) is not
        # None else True)

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)
