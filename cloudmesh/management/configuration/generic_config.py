from os import mkdir
from os.path import isfile, expanduser, dirname, exists

import oyaml as yaml


class GenericConfig(object):

    def __init__(self, config_path):
        """
        Initialize the Config class.

        :param config_path: A local file path to a yaml config
            with a root element `cloudmesh`. Default: `~/.cloudmesh/cloudmesh.yaml`
        """
        self._conf_dict = {}
        self.config_path = expanduser(config_path)
        config_folder = dirname(self.config_path)

        if not exists(config_folder):
            mkdir(config_folder)

        if not isfile(self.config_path):
            open(self.config_path, 'a').close()

        with open(self.config_path, "r") as stream:
            self._conf_dict = yaml.load(stream, Loader=yaml.SafeLoader)
            if self._conf_dict is None:
                self._conf_dict = {}

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
        # BUG: dict and set operations are different
        self._conf_dict.set(key, value)
        with open(self.config_path, "w") as stream:
            yaml.safe_dump(dict(self._conf_dict), stream,
                           default_flow_style=False)

    def deep_set(self, keys, value=None):
        """
        A helper function for setting values in the config without
        a chain of `set()` calls.

        Usage:
            mongo_conn = conf.get('db.mongo.MONGO_CONNECTION_STRING', "https://localhost:3232")

        :param keys: A string representing the value's path in the config.
        :param value: value to be set.
        """
        pointer = self._conf_dict
        inner_dict = pointer
        end = len(keys) - 1
        for index, component in enumerate(keys):
            if index < end or value is None:
                inner_dict = inner_dict.setdefault(component, {})
            else:
                if component not in inner_dict.keys() or type(
                    inner_dict[component]) != dict:
                    inner_dict[component] = value
                else:
                    inner_dict[component].update(value)
        with open(self.config_path, "w") as stream:
            yaml.safe_dump(dict(self._conf_dict), stream,
                           default_flow_style=False)

    def keys(self):
        """
        Print the key names
        :return:
        """
        return self._conf_dict.keys()

    def remove(self, path, key_to_remove):
        """

        :return:
        """
        pointer = self._conf_dict
        inner_dict = pointer
        for key in path:
            inner_dict = inner_dict[key]
        try:
            inner_dict.pop(key_to_remove)
        except KeyError:
            print("{} doesn't exist to remove.".format(key_to_remove))
        with open(self.config_path, "w") as stream:
            yaml.safe_dump(dict(self._conf_dict), stream,
                           default_flow_style=False)
