from deprecated.draft.openstack import OpenstackCM
from deprecated.draft.vm.api.Cloud import Cloud


class Cmopenstack(Cloud):

    def __init__(self, config, cloud):
        # print(cloud)
        self.config = config
        self.driver = OpenstackCM(cloud)  # cloud is chameleon
