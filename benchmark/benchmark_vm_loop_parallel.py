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
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.configuration.Config import Config
from cloudmesh.management.configuration.name import Name
from cloudmesh.common.console import Console
from cloudmesh.common.StopWatch import StopWatch
import time
from multiprocessing import Pool
import sys
from pprint import pprint

batch = 10
sleep = 60

Benchmark.debug()

user = Config()["cloudmesh.profile.user"]
variables = Variables()
VERBOSE(variables.dict())

cloud = variables.parameter('cloud')

print(f"Test run for {cloud}")

if cloud is None:
    raise ValueError("cloud is not not set")

name_generator = Name()
name_generator.set(f"benchmark-{user}-vm-" + "{counter}")
# name_generator.reset()

name = str(name_generator)

provider = Provider(name=cloud)


def Print():
    data = provider.list()
    print(provider.Print(data=data, output='table', kind='vm'))


current_vms = 0

repeat = 100


def generate_names(n):
    names = []
    for i in range(0, n):
        name_generator.incr()
        names.append(str(name_generator))
    return names


def generate_ips(n):
    ips = provider.list_public_ips(available=True)
    if len(ips) < n:
        raise ValueError("Not enough free ips")
    found = []
    for ip in ips[0:n]:
        found.append(ip['floating_ip_address'])
    return found


def list():
    Print()
    data = provider.list()  # update the db


def provider_vm_create(name, ip):
    HEADING()

    try:
        print("start", name, ip)

        StopWatch.start(f"start {name}")
        parameter = {
            'name': name,
            'ip': ip
        }
        data = provider.create(**parameter)
        StopWatch.stop(f"start {name}")

    except Exception as e:
        Console.error(f"could not create VM {name}", traceflag=True)
        print(e)


def provider_vm_terminate(name):
    HEADING()
    try:
        StopWatch.start(f"terminate {name}")
        print("terminate", name)
        data = provider.destroy(name)
        StopWatch.stop(f"terminate {name}")

    except Exception as e:
        Console.error(f"could not terminate VM {name}", traceflag=True)
        print(e)


def create_terrminate(parameters):
    name = parameters['name']
    ip = parameters['ip']
    provider_vm_create(name, ip)
    time.sleep(sleep)
    provider_vm_terminate(name)
    return name


def test_benchmark():
    StopWatch.benchmark(sysinfo=False, csv=False, tag=cloud)


pool = Pool()

p = {}
names = generate_names(batch)
ips = generate_ips(batch)

print(names)
print(ips)

parameter = []
for i in range(0, batch):
    parameter.append(
        {
            'name': names[i],
            'ip': ips[i]
        }
    )

results = pool.map(create_terrminate, parameter)
pool.close()
pool.join()
# print (results)


test_benchmark()
