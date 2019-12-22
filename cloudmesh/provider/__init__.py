from cloudmesh.common.console import Console
from pprint import pprint
from cloudmesh.common.variables import Variables
from cloudmesh.common.debug import VERBOSE


class ComputeProviderPlugin(object):
    pass


class Provider(object):

    def __init__(self):
        self.data = dict()
        self.load()

    def load(self):
        providers = ComputeProviderPlugin.__subclasses__()
        for provider in providers:
            self.data[provider.kind] = provider

    def __getitem__(self, key):
        try:
            return self.data[key]
        except:
            name = f"cloudmesh.compute.{key}.Provider"
            provider = __import__(name)
            self.load()
            # self.data[key] = provider
            variables = Variables()
            if variables['debug'] == 'False':
                Console.cprint("BLUE", "", f"Loading Provider: '{key}'")
            return self.data[key]
