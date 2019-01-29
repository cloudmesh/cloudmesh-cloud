from cloudmesh.openstack.OpenstackCM import OpenstackCM
from cloudmesh.vm.api.Cloud import Cloud


class Cmopenstack(Cloud):

    def __init__(self, config, cloud):
        # print(cloud)
        self.driver = OpenstackCM(cloud)  # cloud is chameleon
