import oyaml as yaml
from os.path import isfile, expanduser, join, dirname, realpath, exists
from cm4.configuration.dot_dictionary import DotDictionary
from shutil import copyfile
from os import mkdir


class GenericConfig(object):

    def __init__(self, config_path):
        """
        Initialize the Config class.

        :param config_path: A local file path to a yaml config
            with a root element `cloudmesh`. Default: `~/.cloudmesh/cloudmesh4.yaml`
        """
        self._conf_dict = {}

        self.config_path = expanduser(config_path)
        config_folder = dirname(self.config_path)

        if not exists(config_folder):
            mkdir(config_folder)

        if not isfile(self.config_path):
            open(self.config_path, 'a').close()

        with open(self.config_path, "r") as stream:
            try:
                self._conf_dict = DotDictionary(yaml.load(stream))
            except TypeError:
                self._conf_dict = DotDictionary()


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
        return self._conf_dict.get(key, default)

    def set(self, key, value):
        """
        A helper function for setting values in the config without
        a chain of `set()` calls.

        Usage:
            mongo_conn = conf.get('db.mongo.MONGO_CONNECTION_STRING', "https://localhost:3232")

        :param key: A string representing the value's path in the config.
        :param value: value to be set.
        """
        self._conf_dict.set(key, value)
        with open(self.config_path, "w") as stream:
            yaml.safe_dump(dict(self._conf_dict), stream, default_flow_style=False)

    def deep_set(self, keys,value):
        """
        A helper function for setting values in the config without
        a chain of `set()` calls.

        Usage:
            mongo_conn = conf.get('db.mongo.MONGO_CONNECTION_STRING', "https://localhost:3232")

        :param key: A string representing the value's path in the config.
        :param value: value to be set.
        """
        tmp_dic = self._conf_dict
        for key in keys[:-1]:
            if key not in tmp_dic:
                tmp_dic[key] = DotDictionary()
                tmp_dic=tmp_dic[key]
        tmp_dic.set(keys[-1], value)
        with open(self.config_path, "w") as stream:
            yaml.safe_dump(dict(self._conf_dict), stream, default_flow_style=False)

    def keys(self):
        """
        Print keys of a subkey
        :param key:
        :return:
        """
        return self._conf_dict.keys()

