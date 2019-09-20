###############################################################
# pytest -v --capture=no tests/1_local/test_04_sec_command.py
# pytest -v  tests/1_local/test_04_sec_command.py
###############################################################
#
# The following commands are tested on the local database
#
# cms sec clear
# cms sec load
# cms rule add
# cms sec rule delete deleteme
# cms sec group add deleteme empty empty
# cms sec group delete deleteme
# cms sec rule list
# cms sec list
# cms sec group list
#
###############################################################


#
# this test is wron as we only want to test the cloud, we need to make sure
# the local is loaded
#
# the local test is in 1_local
#

import pytest
from sys import platform
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables
from cloudmesh.common3.Benchmark import Benchmark
from cloudmesh.common3.Shell import Shell
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.secgroup.Secgroup import Secgroup
from cloudmesh.secgroup.Secgroup import SecgroupExamples
from cloudmesh.secgroup.Secgroup import SecgroupRule

Benchmark.debug()

variables = Variables()
cloud = variables.parameter('cloud')

rules = SecgroupRule()
groups = Secgroup()

cm = CmDatabase()
provider = Provider(name=cloud)


def run(command):
    if platform == 'win32':
        result = Shell.run2(command)
    else:
        result = Shell.run(command)

    print(result)
    return result


@pytest.mark.incremental
class TestSecCLI:

    def test_sec_clear(self):

        cm.clear(collection=f"local-secgroup")
        cm.clear(collection=f"local-secrule")

    def test_group_add(self):
        HEADING()

        Benchmark.Start()
        result = run(f"cms sec group add deleteme empty empty")
        Benchmark.Stop()
        entry = groups.list(name="deleteme")
        assert len(entry) > 0
        assert entry[0]["name"] == "deleteme"

    def test_group_delete(self):
        HEADING()
        Benchmark.Start()
        result = run(f"cms sec group delete deleteme")
        Benchmark.Stop()
        entry = groups.list(name="deleteme")

        assert len(entry) == 0

    def test_sec_init(self):
        HEADING()
        r = rules.clear()
        g = groups.clear()

        examples = SecgroupExamples()
        examples.load()

        assert len(examples.secgroups) > 0
        assert len(examples.secrules) > 0

        result = run(f"cms sec rule add deleteme 101 101 tcp 10.0.0.0/0")

        try:
            result = run(f"cms sec group add wrong nothing wrong")
            assert False
        except:
            assert True

    def test_sec_add_group_wrong(self):
        HEADING()
        try:
            result = run(f"cms sec group load wrong --cloud={cloud}")
            assert False
        except:
            assert True

    def test_cms_init(self):
        HEADING()
        Benchmark.Start()
        result = run(f"cms init")
        Benchmark.Stop()

    def test_sec_list(self):
        HEADING()

        Benchmark.Start()
        result = run("cms sec list")
        Benchmark.Stop()
        # g = groups.list()

        g = rules.list()

        for entry in g:
            name = entry['name']
            if name != 'default':
                assert name in result

    def test_sec_group_list_local(self):
        HEADING()
        Benchmark.Start()
        result = run("cms sec group list")
        Benchmark.Stop()
        g = groups.list()

        for entry in g:
            name = entry['name']
            assert name in result

    def test_sec_group_list_cloud(self):
        HEADING()
        Benchmark.Start()
        result = run(f"cms sec group list --cloud={cloud}")
        Benchmark.Stop()
        g = groups.list()

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=False, tag=cloud)


class a:

    def test_rule_load_to_cloud(self):
        HEADING()
        Benchmark.Start()
        result = run(f"cms sec group load deleteme --cloud={cloud}")
        Benchmark.Stop()


    #        Pro
    #        entry = rules.list(name="deleteme")
    #        assert len(entry) > 0
    #        assert entry[0]["name"] == "deleteme"

    def test_rule_delete(self):
        HEADING()
        Benchmark.Start()
        result = run(f"cms sec rule delete deleteme")
        Benchmark.Stop()
        entry = rules.list(name="deleteme")

        assert len(entry) == 0

    def test_rule_list(self):
        HEADING()

        Benchmark.Start()
        result = run("cms sec rule list")
        Benchmark.stop()
        r = rules.list()
        g = groups.list()

        for entry in r:
            name = entry['name']
            assert name in result
        for entry in g:
            name = entry['name']
            assert name in result
