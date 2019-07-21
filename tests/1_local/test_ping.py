###############################################################
# pytest -v --capture=no tests/1_local/test_name.py
# pytest -v  tests/1_local/test_name.py
# pytest -v --capture=no  tests/1_local/test_name.py:Test_name.<METHIDNAME>
###############################################################

import pytest
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common3.host import Host
from cloudmesh.common.Printer import Printer

# multiping only works if you have root, so we can not use it
# from multiping import MultiPing

hosts = ['127.0.0.1',
         'www.goole.com',
         'www.indiana.edu',
         'www.pbs.org',
         'www.github.com',
         'www.dw.com',
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
        StopWatch.start("total _ping")

        for host in hosts:
            location = {
                'ip': host,
                'count': 1,
            }

            StopWatch.start(f"ping {host}")
            r = Host._ping(location)
            StopWatch.stop(f"ping {host}")

            StopWatch.stop("total _ping")

    def test_ping_processor(self):

        print ()
        for processors in range(1,len(hosts)):
            print ("Processors:", processors)
            r = self.ping(processors=processors)
            print (Printer.write(r,
                                 order=['host',
                                         'success',
                                         'max',
                                         'min',
                                         'stddev']
                                 ))


    #
    # only works if you have root, so not suitable
    #
    # def test_multi_ping(self):
    #     ping = MultiPing(hosts)
    #     responses, no_responses = ping(hosts, timeout=2, retry=1)

    def test_benchmark(self):
        StopWatch.benchmark(sysinfo=False)

