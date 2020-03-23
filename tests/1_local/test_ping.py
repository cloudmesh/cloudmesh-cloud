###############################################################
# pytest -v --capture=no tests/1_local/test_name.py
# pytest -v  tests/1_local/test_name.py
# pytest -v --capture=no  tests/1_local/test_name..py::Test_name::<METHODNAME>
###############################################################

import pytest
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.Host import Host
from cloudmesh.common.Printer import Printer
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
import sys

Benchmark.debug()

cloud = "local"

# multiping only works if you have root, so we can not use it
# from multiping import MultiPing

hosts = ['127.0.0.1',
         'localhost',
         'www.indiana.edu',
         'www.pbs.org',
         'www.github.com',
         'www.redhat.com',
         'www.openstack.org',
         'www.bbc.com',
         'www.ec2instances.info',
         'aws.amazon.com']


@pytest.mark.incremental
class TestPing:

    def ping(self, processors=1):
        StopWatch.start(f"total p={processors} c=1")
        r = Host.ping(hosts, processors=processors, count=1)
        StopWatch.stop(f"total p={processors} c=1")

        return r

    def test_internal_ping(self):
        HEADING()
        StopWatch.start("total _ping")

        for host in hosts:
            location = {
                'ip': host,
                'count': 1,
            }

            StopWatch.start(f"ping {host}")
            result = Host._ping(location)
            StopWatch.stop(f"ping {host}")

            StopWatch.stop("total _ping")
            if b'Access denied' in result['stdout'] and sys.platform == "win32":
                print("ERROR: This test must be run in an administrative "
                      "terminal")
            assert result['success']

    def test_ping_processor(self):
        HEADING()
        print()
        for processors in range(1, len(hosts)):
            print("Processors:", processors)
            results = self.ping(processors=processors)
            print(Printer.write(results,
                                order=['host',
                                       'success',
                                       'max',
                                       'min',
                                       'stddev']
                                ))
            for result in results:
                assert result['success']

    #
    # only works if you have root, so not suitable
    #
    # def test_multi_ping(self):
    #     ping = MultiPing(hosts)
    #     responses, no_responses = ping(hosts, timeout=2, retry=1)

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag=cloud)
