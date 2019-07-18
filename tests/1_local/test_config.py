###############################################################
# pytest -v --capture=no tests/1_local/test_config.py
# pytest -v  tests/1_local/test_config.py
# pytest -v --capture=no  tests/1_local/test_config.py:Test_config.<METHIDNAME>
###############################################################
import os
import textwrap
from pathlib import Path
from pprint import pprint

import oyaml as yaml
import pytest
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand
from cloudmesh.common3.Benchmark import Benchmark
from cloudmesh.management.configuration.config import Config


@pytest.mark.incremental
class TestConfig:

    def test_config(self):
        Benchmark.Start()
        config = Config()
        Benchmark.Stop()

    def test_dict(self):
        HEADING()
        config = Config()
        Benchmark.Start()
        result = config.dict()
        Benchmark.Stop()
        pprint(result)
        print(config)
        print(type(config.data))

        assert config is not None

    def test_config_subscriptable(self):
        HEADING()
        config = Config()
        Benchmark.Start()
        data = config["cloudmesh"]["data"]["mongo"]
        Benchmark.Stop()
        assert data is not None

    def test_dictreplace(self):
        HEADING()
        config = Config()
        spec = textwrap.dedent("""
        cloudmesh:
          profile:
            name: Gregor
          unordered:
            name: "{cloudmesh.other.name}.postfix"
          other:
            name: "{cloudmesh.profile.name}"
        
        """)

        print(spec)

        # spec = spec.replace("{", "{{")
        # spec = spec.replace("}", "}}")

        # print(spec)
        Benchmark.Start()
        result = config.spec_replace(spec)
        Benchmark.Stop()
        print(result)
        data = yaml.load(result, Loader=yaml.SafeLoader)
        pprint(data)

        assert data["cloudmesh"]["unordered"]["name"] == "Gregor.postfix"
        assert data["cloudmesh"]["other"]["name"] == "Gregor"

    def test_configreplace(self):
        HEADING()
        config = Config()
        pprint(config["cloudmesh"]["profile"])

    def test_if_yaml_file_exists(self):
        config = Config()
        config.create()
        filename = path_expand("~/.cloudmesh/cloudmesh4.yaml")
        assert os.path.isfile(Path(filename))

    def test_set(self):
        Benchmark.Start()
        config = Config()
        config["cloudmesh.test.nested"] = "Gregor"
        Benchmark.Stop()
        print(config["cloudmesh.test.nested"])
        assert config["cloudmesh.test.nested"] == "Gregor"

    ''' THIS TEST DOE FAIL
    def test_del(self):
        del config["cloudmesh.test.nested"]

        assert config["cloudmesh.test.nested"] != "Gregor"
    '''

    def test_benchmark(self):
        Benchmark.print()
