###############################################################
# pytest -v --capture=no tests/1_basic/test_sec_command.py
# pytest -v  tests/1_basic/test_sec_command.py
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
# the local test is in 1_basic
#

import pytest
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables
from cloudmesh.common3.Shell import Shell
from cloudmesh.secgroup.Secgroup import Secgroup
from cloudmesh.secgroup.Secgroup import SecgroupExamples
from cloudmesh.secgroup.Secgroup import SecgroupRule



variables = Variables()
cloud = variables.parameter('cloud')

rules = SecgroupRule()
groups = Secgroup()



def run(label, command):
    result = Shell.run_timed(label, command, service=cloud)
    print(result)
    return result


@pytest.mark.incremental
class TestSecCLI:

    def test_init(self):

        r = rules.clear()
        g = groups.clear()

        examples = SecgroupExamples()
        examples.load()

        assert len(examples.secgroups) > 0
        assert len(examples.secrules) > 0


        result = run("rule add",
                     f"cms sec rule add deleteme 101 101 tcp 10.0.0.0/0")

        result = run("group add",
                     f"cms sec group add wrong nothing wrong")

    def test_add_group(self):
        result = run("group add",
                     f"cms sec group load wrong --cloud={cloud}")


class a:

    def test_rule_load_to_cloud(self):
        HEADING()

        result = run("rule add",
                     f"cms sec group load deleteme --cloud={cloud}")

class o:

#        Pro
#        entry = rules.list(name="deleteme")
#        assert len(entry) > 0
#        assert entry[0]["name"] == "deleteme"


    def test_rule_delete(self):
        HEADING()

        result = run("rule delete", f"cms sec rule delete deleteme")
        entry = rules.list(name="deleteme")

        assert len(entry) == 0

    def test_group_add(self):
        HEADING()

        result = run("group add", f"cms sec group add deleteme empty empty")
        entry = groups.list(name="deleteme")

        assert len(entry) > 0
        assert entry[0]["name"] == "deleteme"

    def test_group_delete(self):
        HEADING()

        result = run("group delete", f"cms sec group delete deleteme")
        entry = groups.list(name="deleteme")

        assert len(entry) == 0

    def test_rule_list(self):
        HEADING()

        result = run("rule list", "cms sec rule list")
        r = rules.list()
        g = groups.list()

        for entry in r:
            name = entry['name']
            assert name in result
        for entry in g:
            name = entry['name']
            assert name in result

    def test_list(self):
        HEADING()

        result = run("list", "cms sec list")
        g = groups.list()

        for entry in g:
            name = entry['name']
            assert name in result

    def test_group_list(self):
        HEADING()

        result = run("list", "cms sec group list")
        g = groups.list()

        for entry in g:
            name = entry['name']
            assert name in result

    def test_benchmark(self):
        StopWatch.benchmark()
