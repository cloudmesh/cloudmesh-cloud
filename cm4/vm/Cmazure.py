from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from cm4.vm.Cloud import Cloud


class Cmazure(Cloud):

    def __init__(self, config, cloud):
        cls = get_driver(Provider.AZURE_ARM)
        os_config = config.get('cloud.%s' % cloud)
        default = os_config.get('default')
        credentials = os_config.get('credentials')
        self.driver = cls(
            tenant_id=credentials['AZURE_TENANT_ID'],
            subscription_id=credentials['AZURE_SUBSCRIPTION_ID'],
            key=credentials['AZURE_APPLICATION_ID'],
            secret=credentials['AZURE_SECRET_KEY'],
            region=default['region']
        )
