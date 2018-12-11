from cm4.openstack.OpenstackCM import OpenstackCM
from cm4.vm.Cloud import Cloud


class Cmopenstack(Cloud):

    def __init__(self, config, cloud):
        # print(cloud)
        self.driver = OpenstackCM(cloud)  # cloud is chameleon
