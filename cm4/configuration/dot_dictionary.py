import collections.abc


class DotDictionary(dict):
    """
    A subclass of `dict` that allows dot paths into nested dictionary.

    Based on: https://stackoverflow.com/a/2390997/120783

    Usage:
        dot = DotDictionary({'meta': {'status': 'OK', 'status_code': 200}})
        sc = dot.get('meta.status_code')
        sc2 = dot['meta.status_code']
    """

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __getitem__(self, key, default=None):
        """
        A helper function for reading values from the config without
        a chain of `get()` calls.

        Usage:
            mongo_conn = conf.get('db.mongo.MONGO_CONNECTION_STRING')
            default_db = conf.get('default.db')
            az_credentials = conf.get('data.service.azure.credentials')

        :param key: A string representing the value's path in the config.
        """
        val = self._deep_get(self, key.split("."), default)
        return DotDictionary(val) if val and type(val) is dict else val

    def get(self, key, default=None):
        return self.__getitem__(key, default)

    def set(self, key, value):
        self._deep_set(key.split("."), value)

    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)

    def __repr__(self):
        dictrepr = dict.__repr__(self)
        return '%s(%s)' % (type(self).__name__, dictrepr)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v

    def _deep_get(self, d, keys, default=None):
        """
        A helper for getting values from nested dictionaries.

        Based on: https://stackoverflow.com/a/50173148/120783

        Example:
            d = {'meta': {'status': 'OK', 'status_code': 200}}
            deep_get(d, ['meta', 'status_code'])          # => 200
            deep_get(d, ['garbage', 'status_code'])       # => None
            deep_get(d, ['meta', 'garbage'], default='-') # => '-'
        """
        if d is None:
            return default
        elif not keys:
            return d

        try:
            return self._deep_get(dict.get(d, keys[0]), keys[1:], default)
        except KeyError:
            return default

    def _deep_set(self, keys, value):
        """
        A helper for setting values from nested dictionaries.

        Example:
            Keys = {'meta': {'status': 'OK', 'status_code': 200}}
            deep_set(['meta', 'status_code'], 300)          # => {'meta': {'status': 'OK', 'status_code': 300}}
        """
        if len(keys) < 1 or keys[0] == "":
            return
        elif len(keys) == 1:
            self[keys[0]] = value
        else:
            temp_dict = self.setdefault(keys[0])
            for key in keys[1:-1]:
                temp_dict = temp_dict.setdefault(key, {})
            temp_dict[keys[-1]] = value

    def to_dict(self, input=None):
        if input is None:
            input = self
        if isinstance(input, collections.abc.Mapping):
            return {k: self.to_dict(v) for k, v in input.items()}
        else:
            return input
