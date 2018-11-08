from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from cm4.vm.Cloud import Cloud


class Cmaws(Cloud):

    def __init__(self, config, kind):
        cls = get_driver(Provider.EC2)
        os_config = config.get('cloud.%s' % kind)
        default = os_config.get('default')
        credentials = os_config.get('credentials')
        self.driver = cls(credentials['EC2_ACCESS_ID'],
                     credentials['EC2_SECRET_KEY'],
                     region=default['region'])


        '''
        size = [s for s in driver.list_sizes() if s.id == default['size']][0]
        image = [i for i in driver.list_images() if i.id == default['image']][0]
        self.setting = dict(image=image, size=size, ex_keyname=default['EC2_PRIVATE_KEY_FILE_NAME'],
                            ex_securitygroup=default['EC2_SECURITY_GROUP'])
        '''



    '''
    def get_new_node_setting(self):
        return self.setting
    '''

    def get_provider(self):
        return self.driver


