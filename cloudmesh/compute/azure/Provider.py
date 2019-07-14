from cloudmesh.compute.libcloud import Provider as LibCloudProvider


class Provider(LibCloudProvider):

    kind = "azure_libcloud_b"

    def __init__(self, name=None, configuration="~/.cloudmesh/.cloudmesh4.yaml"):
        super().__init__(name=name, configuration=configuration)
