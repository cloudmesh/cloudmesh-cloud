import cloudmesh.storage.provider.gdrive.Provider
import cloudmesh.storage.provider.box.Provider

class Manager(object):

    def __init__(self):
        print("init {name}".format(name=self.__class__.__name__))

    def _provider(self, service):
        provider = None
        if service == "gdrive":
            provider = cloudmesh.storage.provider.gdrive.Provider.Provider()
        elif service == "box":
            provider = cloudmesh.storage.provider.box.Provider.Provider()
        return provider

    def list(self, parameter):
        print("list", parameter)
        provider = self._provider(service)

    def delete(self, filename):
        print ("delete filename")
        provider = self._provider(service)
        provider.delete(filename)

    def get(self, service, filename):
        print("get", service, filename)
        provider = self._provider(service)
        provider.get(filename)

    def put(self, service, filename):
        print("put", service, filename)
        provider = self._provider(service)
        provider.put(filename)
