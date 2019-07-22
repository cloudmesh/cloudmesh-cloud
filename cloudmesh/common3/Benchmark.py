import inspect
import os
from pprint import pprint

import yaml
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.util import path_expand


# noinspection PyPep8Naming
class Benchmark(object):

    @staticmethod
    def name():
        """
        name of the calling method

        :return: the name
        """
        frame = inspect.getouterframes(inspect.currentframe())
        method = frame[2][3]
        return method

    @staticmethod
    def Start():
        """
        starts a timer while using the name of the calling method
        """
        StopWatch.start(Benchmark.name())

    @staticmethod
    def Stop():
        """
        stops a timer while using the name of the calling method
        """
        StopWatch.stop(Benchmark.name())

    @staticmethod
    def print(sysinfo=True):
        """
        prints the benchmark information with all timers
        """
        StopWatch.start("benchmark_start_stop")
        StopWatch.stop("benchmark_start_stop")

        StopWatch.benchmark(sysinfo=sysinfo)

    @staticmethod
    def yaml(path, n):
        """
        creates a cloudmesh service yaml test file

        Example: BenchmarkFiles.yaml("./t.yaml", 10)

        :param path: the path
        :param n: number of services
        :return:
        """
        cm = {
            "cloudmesh": {}
        }
        for i in range(0, n):
            cm["cloudmesh"][f"service{i}"] = {
                "attribute": f"service{i}"
            }
        pprint(cm)
        location = path_expand(path)

        with open(location, 'w') as yaml_file:
            yaml.dump(cm, yaml_file, default_flow_style=False)

    # noinspection SpellCheckingInspection
    @staticmethod
    def file(path, n):
        """
        create a file of given size in MB, the MB here is in binary not SI
        units.
        e.g. 1,048,576 Bytes

        Example: s = BenchmarkFiles.size("./sise.txt", 2)
                 print(s)

        :param path: the filename and path
        :type path: string
        :param n: the size in binary MB
        :type n: integer
        :return: size in MB
        :rtype: float
        """
        location = path_expand(path)
        size = 1048576 * n  # size in bytes
        with open(path, "wb") as f:
            f.write(os.urandom(size))

        s = os.path.getsize(location)
        # try:
        #    os.system(f"ls -lhs {location}")
        #    os.system(f"du -h {location}")
        # except:
        #    pass

        return s / 1048576.0
