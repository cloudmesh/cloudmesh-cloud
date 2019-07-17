from pprint import pprint

import pytest
from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import HEADING
from cloudmesh.management.configuration.name import Name
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.management.configuration.config import Config
from cloudmesh.common3.Shell import Shell
from cloudmesh.secgroup.Secgroup import Secgroup
from cloudmesh.secgroup.Secgroup import SecgroupExamples
from cloudmesh.secgroup.Secgroup import SecgroupRule
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.debug import VERBOSE

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

        run("clear", "cms sec clear")

        r = rules.list()
        g = groups.list()

        assert len(r) == 0
        assert len(g) == 0

    def test_load(self):
        run("load", "cms sec load")

        r = rules.list()
        g = groups.list()

        assert len(r) > 0
        assert len(g) > 0

        examples = SecgroupExamples()
        assert len(g) == len(examples.secgroups)
        assert len(r) == len(examples.secrules)

    def test_rule_add(self):
        HEADING()

        result = run("rule add", f"cms sec rule add deleteme FROMPORT TOPORT PROTOCOL CIDR")
        entry = rules.list(name="deleteme")

        assert len(entry) > 0
        assert entry[0]["name"] == "deleteme"

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

