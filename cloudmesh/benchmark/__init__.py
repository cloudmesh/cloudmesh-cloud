import yaml
from cloudmesh.common.util import path_expand
from pprint import pprint

print("LLLL")


class BenchmarkFiles(object):

    @staticmethod
    def yaml(path, n):
        cm = {
            "cloudmesh": {}
        }
        for i in range(0, n):
            cm[f"service{i}"] = {
                "attribute": f"service{i}"
            }
        pprint(cm)
        location = path_expand(path)

        with open(location, 'w') as yaml_file:
            yaml.dump(cm, yaml_file, default_flow_style=False)

    @staticmethod
    def size(path, n):
        pass


print("lll")
BenchmarkFiles.yaml("./t.yaml", 10)
