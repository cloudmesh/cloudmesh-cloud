from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.base import NodeAuthSSHKey
from cm4.vm.Cloud import Cloud


class Cmazure(Cloud):

    def __init__(self, config, cloud):
        cls = get_driver(Provider.AZURE_ARM)
        os_config = config.get('cloud.%s' % cloud)
        default = os_config.get('default')
        credentials = os_config.get('credentials')
        self.driver = cls(tenant_id=credentials['AZURE_TENANT_ID'],
                     subscription_id=credentials['AZURE_SUBSCRIPTION_ID'],
                     key=credentials['AZURE_APPLICATION_ID'],
                     secret=credentials['AZURE_SECRET_KEY'],
                     region=default['region'])
        '''
        size = [s for s in driver.list_sizes() if s.id == default['size']][0]
        image = [i for i in driver.list_images() if i.id == default['image']][0]
        self.setting = dict(size=size, image=image, auth=NodeAuthSSHKey(default['AZURE_MANAGEMENT_CERT_PATH']),
                            ex_use_managed_disks=True, ex_resource_group=default['resource_group'],
                            ex_storage_account=default['storage_account'],
                            ex_network=default['network']
                            )
        '''


    '''
    def get_new_node_setting(self):
        return self.setting
    '''
