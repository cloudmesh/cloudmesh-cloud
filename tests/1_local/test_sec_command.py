###############################################################
# pytest -v --capture=no tests/1_local/test_sec_command.py
# pytest -v  tests/1_local/test_sec_command.py
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


import pytest
from cloudmesh.common.util import HEADING
from cloudmesh.common3.Benchmark import Benchmark
from cloudmesh.common3.Shell import Shell
from cloudmesh.secgroup.Secgroup import Secgroup
from cloudmesh.secgroup.Secgroup import SecgroupExamples
from cloudmesh.secgroup.Secgroup import SecgroupRule

Benchmark.debug()

rules = SecgroupRule()
groups = Secgroup()


def run(label, command):
    result = Shell.run_timed(label, command, service="local")
    print(result)
    return result


@pytest.mark.incremental
class TestSecCLI:

    def test_clear(self):
        HEADING(color="HEADER")

        Benchmark.Start()
        run("clear", "cms sec clear")
        Benchmark.Stop()

        r = rules.list()
        g = groups.list()

        assert len(r) == 0
        assert len(g) == 0

    def test_load(self):
        HEADING()
        Benchmark.Start()
        run("load", "cms sec load")
        Benchmark.Stop()

        r = rules.list()
        g = groups.list()

        assert len(r) > 0
        assert len(g) > 0

        examples = SecgroupExamples()
        assert len(g) == len(examples.secgroups)
        assert len(r) == len(examples.secrules)

    def test_rule_add(self):
        HEADING()

        Benchmark.Start()
        result = run("rule add",
                     f"cms sec rule add deleteme FROMPORT TOPORT PROTOCOL CIDR")
        Benchmark.Stop()

        entry = rules.list(name="deleteme")

        assert len(entry) > 0
        assert entry[0]["name"] == "deleteme"

    def test_rule_delete(self):
        HEADING()

        Benchmark.Start()
        result = run("rule delete", f"cms sec rule delete deleteme")
        Benchmark.Stop()

        entry = rules.list(name="deleteme")

        assert len(entry) == 0

    def test_group_add(self):
        HEADING()

        Benchmark.Start()
        result = run("group add", f"cms sec group add deleteme empty empty")
        Benchmark.Stop()

        entry = groups.list(name="deleteme")

        assert len(entry) > 0
        assert entry[0]["name"] == "deleteme"

    def test_group_delete(self):
        HEADING()

        Benchmark.Start()
        result = run("group delete", f"cms sec group delete deleteme")
        Benchmark.Stop()

        entry = groups.list(name="deleteme")

        assert len(entry) == 0

    def test_rule_list(self):
        HEADING()

        Benchmark.Start()
        result = run("rule list", "cms sec rule list")
        Benchmark.Stop()

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

        Benchmark.Start()
        result = run("list", "cms sec list")
        Benchmark.Stop()

        g = groups.list()

        for entry in g:
            name = entry['name']
            assert name in result

    def test_group_list(self):
        HEADING()

        Benchmark.Start()
        result = run("list", "cms sec group list")
        Benchmark.Stop()

        g = groups.list()

        for entry in g:
            name = entry['name']
            assert name in result

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True)
