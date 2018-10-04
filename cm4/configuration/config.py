import oyaml as yaml
from os.path import isfile, expanduser
from cm4.configuration.dot_dictionary import DotDictionary


class Config(object):

    def __init__(self, config_path='~/.cloudmesh/cloudmesh4.yaml'):
        """
        Initialize the Config class.

        :param config_path: A local file path to cloudmesh yaml config
            with a root element `cloudmesh`. Default: `~/.cloudmesh/cloudmesh4.yaml`
        """
        self._cloudmesh = {}

        config_path = expanduser(config_path)

        if not isfile(config_path):
            raise Exception(f"`{config_path}` is not a file.")

        with open(config_path, "r") as stream:
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
