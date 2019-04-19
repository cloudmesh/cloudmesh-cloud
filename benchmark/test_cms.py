###############################################################
# pytest -v --capture=no benchmark/test_cms.py
# pytest -v  benchmark/test_cms.py
# pytest -v --capture=no benchmark/test_cms.py:Test_cms.<METHIDNAME>
###############################################################
import os
import sys
import platform

import pytest
from cloudmesh.DEBUG import VERBOSE
from cloudmesh.common.Printer import Printer
from cloudmesh.common.Shell import Shell
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.util import HEADING
from cloudmesh.common.systeminfo import systeminfo
from pprint import pprint


@pytest.mark.incremental
class TestConfig:

    def test_help(self):
        HEADING()

        StopWatch.start("cms help")
        result = Shell.execute("cms help", shell=True)
        StopWatch.stop("cms help")

        VERBOSE(result)

        assert "quit" in result
        assert "clear" in result

    def test_vm(self):
        HEADING()

        StopWatch.start("cms help vm")
        result = Shell.execute("cms help vm", shell=True)
        StopWatch.stop("cms help vm")

        VERBOSE(result)

        assert "['sample1', 'sample2', 'sample3', 'sample18']" in result

    def test_storage(self):
        HEADING()

        StopWatch.start("cms help storage")
        result = Shell.execute("cms help storage", shell=True)
        StopWatch.stop("cms help storage")

        VERBOSE(result)

        assert "storage put SOURCE DESTINATION --recursive" in result

    def test_results(self):
        HEADING()

        #
        # PRINT PLATFORM
        #
        data_platform = systeminfo()
        print(Printer.attribute(data_platform,
                                ["Machine Arribute", "Time/s"]))

        #
        # PRINT TIMERS
        #
        timers = StopWatch.keys()

        data_timers = {}
        for timer in timers:
            data_timers[timer] = {
                'time': round(StopWatch.get(timer), 2),
                'timer': timer
            }
            for attribute in ["node", "system", "machine", "mac_version", "win_version"]:
                data_timers[timer][attribute] = data_platform[attribute]
        #print(Printer.attribute(data_timers, header=["Command", "Time/s"]))
        print(Printer.write(
            data_timers,
            order=["timer", "time", "node", "system", "mac_version", "win_version"]
        ))

        print()
        print(Printer.write(
            data_timers,
            order=["timer", "time", "node", "system", "mac_version", "win_version"],
            output="csv"
        ))
