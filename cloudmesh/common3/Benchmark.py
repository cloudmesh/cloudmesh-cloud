import inspect
from cloudmesh.common.StopWatch import StopWatch
from pprint import pprint
import os

class Benchmark(object):

    @staticmethod
    def name():
        frame =  inspect.getouterframes(inspect.currentframe())
        method = frame[2][3]
        return method

    @staticmethod
    def Start():
        StopWatch.start(Benchmark.name())

    @staticmethod
    def Stop():
        StopWatch.stop(Benchmark.name())

    @staticmethod
    def print():
        StopWatch.start("benchmark_start_stop")
        StopWatch.stop("benchmark_start_stop")

        StopWatch.benchmark()
