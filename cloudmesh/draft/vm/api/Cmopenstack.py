from cloudmesh.draft.openstack import OpenstackCM
from cloudmesh.draft.vm.api.Cloud import Cloud


class Cmopenstack(Cloud):

    def __init__(self, config, cloud):
        # print(cloud)
        self.config = config
        self.driver = OpenstackCM(cloud)  # cloud is chameleon
