import oyaml as yaml
from os.path import isfile, expanduser, join, dirname, realpath, exists
from cm4.configuration.dot_dictionary import DotDictionary
from shutil import copyfile
from os import mkdir


class Config(object):

    def __init__(self, config_path='~/.cloudmesh/cloudmesh4.yaml'):
        """
        Initialize the Config class.

        :param config_path: A local file path to cloudmesh yaml config
            with a root element `cloudmesh`. Default: `~/.cloudmesh/cloudmesh4.yaml`
        """
        self._cloudmesh = {}

        self.config_path = expanduser(config_path)
        config_folder = dirname(self.config_path)

        if not exists(config_folder):
            mkdir(config_folder)

        if not isfile(self.config_path):
            copyfile(join(dirname(realpath(__file__)), "../etc/cloudmesh4.yaml"), self.config_path)

        with open(self.config_path, "r") as stream:
            conf = yaml.load(stream)
            self._cloudmesh = DotDictionary(conf.get('cloudmesh'))

    def get(self, key, default=None):
        """
        A helper function for reading values from the config without
        a chain of `get()` calls.

        Usage:
            mongo_conn = conf.get('db.mongo.MONGO_CONNECTION_STRING')
            default_db = conf.get('default.db')
            az_credentials = conf.get('data.service.azure.credentials')

        :param key: A string representing the value's path in the config.
        """
        return self._cloudmesh.get(key, default)

    def set(self, key, value):
        """
        A helper function for setting values in the config without
        a chain of `set()` calls.

        Usage:
            mongo_conn = conf.get('db.mongo.MONGO_CONNECTION_STRING', "https://localhost:3232")

        :param key: A string representing the value's path in the config.
        :param value: value to be set.
        """
        self._cloudmesh.set(key, value)
        yamlFile = {}
        yamlFile["cloudmesh"] = self._cloudmesh.copy()
        with open(self.config_path, "w") as stream:
            yaml.safe_dump(yamlFile, stream, default_flow_style=False)

