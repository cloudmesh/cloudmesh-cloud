from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from cm4.vm.Cloud import Cloud


class Cmaws(Cloud):

    def __init__(self, config, kind):
        cls = get_driver(Provider.EC2)
        os_config = config.get('cloud.%s' % kind)
        default = os_config.get('default')
        credentials = os_config.get('credentials')
        self.driver = cls(
            credentials['EC2_ACCESS_ID'],
            credentials['EC2_SECRET_KEY'],
            region=default['region']
        )
