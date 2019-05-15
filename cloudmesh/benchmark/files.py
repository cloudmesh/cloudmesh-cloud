import yaml
from cloudmesh.common.util import path_expand
from pprint import pprint
import os


class BenchmarkFiles(object):

    @staticmethod
    def yaml(path, n):
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

    @staticmethod
    def size(path, n):
        """
        create a file of given size in MB, the MB here is in bianry not SI units.
        e.g. 1,048,576 Bytes
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


if __name__ == "__main__":
    BenchmarkFiles.yaml("./t.yaml", 10)
    s = BenchmarkFiles.size("./sise.txt", 2)
    print(s)
