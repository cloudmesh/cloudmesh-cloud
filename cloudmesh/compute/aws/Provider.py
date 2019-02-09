from cloudmesh.compute.libcloud import Provider as LibCloudProvider


class Provider(LibCloudProvider):

    def __init__(self, name=None, configuration="~/.cloudmesh/.cloudmesh4.yaml"):
        super().__init__(name=name, configuration=configuration)
        self.p = LibCloudProvider(name=name, configuration=configuration)

