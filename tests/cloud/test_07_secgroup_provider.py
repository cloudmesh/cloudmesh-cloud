###############################################################
# pytest -v --capture=no tests/cloud/test_05_secgroup_provider.py
# pytest -v  tests/cloud/test_05_secgroup_provider.py
###############################################################

# TODO: start this with cloud init, e.g, empty mongodb
# TODO: assertuons need to be added

import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.configuration.Config import Config
from cloudmesh.management.configuration.name import Name
from cloudmesh.secgroup.Secgroup import Secgroup
from cloudmesh.secgroup.Secgroup import SecgroupExamples
from cloudmesh.secgroup.Secgroup import SecgroupRule

Benchmark.debug()

user = Config()["cloudmesh.profile.user"]
variables = Variables()
VERBOSE(variables.dict())

cloud = variables.parameter('cloud')

print(f"Test run for {cloud}")

if cloud is None:
    raise ValueError("cloud is not not set")


def run(label, command):
    result = Shell.run_timed(label, command, service=cloud)
    print(result)
    return result


name_generator = Name(schema=f"test-{user}-vm", counter=1)

provider = Provider(name=cloud)

rules = SecgroupRule()
groups = Secgroup()
examples = SecgroupExamples()


@pytest.mark.incremental
class Test_secgroup_provider:

    def test_load(self):
        HEADING(color="HEADER")

        r = rules.clear()
        g = groups.clear()

        Benchmark.Start()
        examples.load()
        Benchmark.Stop()

        r = rules.list()
        g = groups.list()

        assert len(g) == len(examples.secgroups)
        assert len(r) == len(examples.secrules)

    def test_list_variables(self):
        HEADING()
        Benchmark.Start()
        print(user)
        print(cloud)
        assert user != "TBD"
        Benchmark.Stop()

    def test_list_secgroups(self):
        HEADING()
        Benchmark.Start()
        groups = provider.list_secgroups()
        Benchmark.Stop()
        provider.Print(groups, output='json', kind="secgroup")

    def test_list_secgroups_rules(self):
        HEADING()
        Benchmark.Start()
        rule_groups = provider.list_secgroups_rules()
        Benchmark.Stop()
        provider.Print(output='json', kind="secgroup", data=rule_groups)

    def test_secgroups_add(self):
        HEADING()
        name = "Test_Sec_Group"
        Benchmark.Start()
        provider.add_secgroup(name=name)
        Benchmark.Stop()
        sec_groups = provider.list_secgroups()
        provider.Print(output='json', kind="secgroup", data=sec_groups)

    def test_upload_secgroup(self):
        HEADING()
        name = "Test_Sec_Group"
        Benchmark.Start()
        provider.upload_secgroup(name=name)
        Benchmark.Stop()
        sec_groups = provider.list_secgroups()
        provider.Print(output='json', kind="secgroup", data=sec_groups)

    def test_secgroups_delete(self):
        HEADING()
        name = "Test_Sec_Group"
        Benchmark.Start()
        provider.remove_secgroup(name=name)
        Benchmark.Stop()
        sec_groups = provider.list_secgroups()
        if cloud == 'aws':
            group_indicator = 'GroupName'
        # elif cloud == 'chameleon':
        else:
            group_indicator = 'name'

        for e in sec_groups:
            print(e[group_indicator])
        provider.Print(output='json', kind="secgroup", data=sec_groups)

    def test_secgroups_delete_again(self):
        HEADING()
        name = "Test_Sec_Group"
        Benchmark.Start()
        provider.remove_secgroup(name=name)
        Benchmark.Stop()
        g = provider.list_secgroups()
        if cloud == 'aws':
            group_indicator = 'GroupName'
        # elif cloud == 'chameleon':
        elif cloud == 'oracle':
            group_indicator = '_display_name'
        else:
            group_indicator = 'name'

        for e in g:
            print(e[group_indicator])
        provider.Print(output='json', kind="secgroup", data=g)

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)
