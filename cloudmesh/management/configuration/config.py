from os import mkdir
from os.path import isfile, expanduser, join, dirname, realpath, exists
from pathlib import Path
from shutil import copyfile
from cloudmesh.terminal.Terminal import VERBOSE
from cloudmesh.common.util import path_expand
import munch
import re
import oyaml as yaml

from cloudmesh.common.dotdict import dotdict
from cloudmesh.shell.variables import Variables


class Active(object):

    def __init__(self, config_path='~/.cloudmesh/cloudmesh4.yaml'):
        self.config = Config(config_path=config_path)

    def clouds(self):
        names = []
        entries = self.config["cloudmesh"]["cloud"]
        for entry in entries:
            if entries[entry]["cm"]["active"]:
                names.append(entry)
        if len(names) == 0:
            names = None
        return names


class Config(object):
    __shared_state = {}

    def __init__(self, config_path='~/.cloudmesh/cloudmesh4.yaml',
                 encrypted=False):
        """
        Initialize the Config class.

        :param config_path: A local file path to cloudmesh yaml config
            with a root element `cloudmesh`. Default: `~/.cloudmesh/cloudmesh4.yaml`
        """

        self.__dict__ = self.__shared_state
        if "data" not in self.__dict__:

            VERBOSE.print("Load config", verbose=9)

            self.config_path = Path(path_expand(config_path)).resolve()
            self.config_folder = dirname(self.config_path)

            if not exists(self.config_folder):
                mkdir(self.config_folder)

            if not isfile(self.config_path):
                source = Path(join(dirname(realpath(__file__)),
                                   "../../etc/cloudmesh4.yaml"))

                copyfile(source.resolve(), self.config_path)

            #with open(self.config_path, "r") as stream:
            #    # self.data = yaml.load(stream, Loader=yaml.FullLoader)
            #    self.data = yaml.load(stream, Loader=yaml.SafeLoader)

            with open(self.config_path, "r") as stream:
                content = stream.read()
                content = path_expand(content)
                content = self.spec_replace(content)
                self.data = yaml.load(content, Loader=yaml.SafeLoader)


            # self.data is loaded as nested OrderedDict, can not use set or get methods directly
            if self.data is None:
                raise EnvironmentError(
                    "Failed to load configuration file cloudmesh4.yaml, please check the path and file locally")

            #
            # populate default variables
            #

            self.variable_database = Variables(filename="~/.cloudmesh/var-data")
            self.set_debug_defaults()

            default = self.default()

            for name in self.default():
                if name not in self.variable_database:
                    self.variable_database[name] = default[name]
            if "cloud" in default:
                self.cloud = default["cloud"]
            else:
                self.cloud = None

    def spec_replace(self, spec):

        variables = re.findall("\{\w.+\}", spec)

        for i in range(0, len(variables)):
            data = yaml.load(spec, Loader=yaml.SafeLoader)

            m = munch.DefaultMunch.fromDict(data)

            for variable in variables:
                text = variable
                variable = variable[1:-1]
                value = eval(f"m.{variable}")
                if "{" not in value:
                    spec = spec.replace(text, value)
        return spec

    def credentials(self, kind, name):
        """

        :param kind: the first level of attributes after cloudmesh
        :param name: the name of the resource
        :return:
        """
        return self.data["cloudmesh"][kind][name]["credentials"]

    def set_debug_defaults(self):
        for name in ["trace", "debug"]:
            if name not in self.variable_database:
                self.variable_database[name] = str(False)

    def dict(self):
        return self.data

    def __str__(self):
        return yaml.dump(self.data, default_flow_style=False, indent=2)

    def get(self, key, default=None):
        """
        A helper function for reading values from the config without
        a chain of `get()` calls.

        Usage:
            mongo_conn = conf.get('db.mongo.MONGO_CONNECTION_STRING')
            default_db = conf.get('default.db')
            az_credentials = conf.get('data.service.azure.credentials')

        :param default:
        :param key: A string representing the value's path in the config.
        """
        return self.data.get(key, default)

    def set(self, key, value):
        # BUG
        """
        A helper function for setting values in the config without
        a chain of `set()` calls.

        Usage:
            mongo_conn = conf.get('db.mongo.MONGO_CONNECTION_STRING', "https://localhost:3232")

        :param key: A string representing the value's path in the config.
        :param value: value to be set.
        """
        self.data['cloudmesh']['default']['cloud'] = value
        print("Setting env parameter cloud to: " + self.data['cloudmesh']['default']['cloud'])

        yaml_file = self.data.copy()
        with open(self.config_path, "w") as stream:
            print("Writing update to cloudmesh.yaml")
            yaml.safe_dump(yaml_file, stream, default_flow_style=False)

    def default(self):
        return dotdict(self.data["cloudmesh"]["default"])

    def __getitem__(self, item):
        """
        gets an item form the dict. The key is . separated
        use it as follows get("a.b.c")
        :param item:
        :type item:
        :return:
        """
        if "." in item:
            keys = item.split(".")
        else:
            return self.data[item]
        element = self.data[keys[0]]
        for key in keys[1:]:
            element = element[key]
        return element
