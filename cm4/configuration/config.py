import oyaml as yaml
from os.path import isfile, expanduser, join, dirname, realpath, exists
from shutil import copyfile
from os import mkdir
from pathlib import Path
from pprint import pprint
from cloudmesh.common.dotdict import dotdict
from cloudmesh.shell.variables import Variables

class Config(object):

    def __init__(self, config_path='~/.cloudmesh/cloudmesh4.yaml'):
        """
        Initialize the Config class.

        :param config_path: A local file path to cloudmesh yaml config
            with a root element `cloudmesh`. Default: `~/.cloudmesh/cloudmesh4.yaml`
        """

        self.config_path = Path(expanduser(config_path)).resolve()
        config_folder = dirname(self.config_path)

        if not exists(config_folder):
            mkdir(config_folder)

        if not isfile(self.config_path):
            destination_path = Path(join(dirname(realpath(__file__)), "../etc/cloudmesh4.yaml"))
            copyfile(destination_path.resolve(), self.config_path)

        with open(self.config_path, "r") as stream:
            self.data = yaml.load(stream)

        # self.data is loaded as nested OrderedDict, can not use set or get methods directly
        if self.data is None:
            raise EnvironmentError(
                "Failed to load configuration file cloudmesh4.yaml, please check the path and file locally")

        #
        # populate default variables
        #
        default = self.default()

        database = Variables(filename="~/.cloudmesh/var-data")

        for name in default:
            if not name in database:
                database[name] = default[name]


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
            print("Writing updata to cloudmesh.yaml")
            yaml.safe_dump(yaml_file, stream, default_flow_style=False)

    def default(self):
        return dotdict(self.data["cloudmesh"]["default"])