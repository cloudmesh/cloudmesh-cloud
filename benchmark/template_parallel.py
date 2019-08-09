from multiprocessing import Pool

from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.console import Console
from cloudmesh.common.util import HEADING
from cloudmesh.common3.Benchmark import Benchmark

batch = 10
sleep = 60

Benchmark.debug()


def generate_parameter(n):
    return range(0, n)


def doit(name):
    HEADING()

    try:
        print("start", name)

        StopWatch.start(f"start {name}")
        # put your code here
        StopWatch.stop(f"start {name}")

    except Exception as e:
        Console.error(f"issue {name}", traceflag=True)
        print(e)

    return name


pool = Pool()

parameter = generate_parameter(batch)
results = pool.map(doit, parameter)
pool.close()
pool.join()
# print (results)

StopWatch.benchmark(sysinfo=True, csv=False, tag="local")
