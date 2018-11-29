from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from cm4.openstack.OpenstackCM import OpenstackCM
from cm4.vm.Cloud import Cloud
import os

class Cmopenstack(Cloud):

    def __init__(self, config, cloud):
#        cls = get_driver(Provider.OPENSTACK)
#        os_config = config.get('cloud.%s' % cloud)
#        credentials = os_config.get('credentials')
        self.driver = OpenstackCM(cloud)
        
#        cls(
#            credentials['OS_USERNAME'],
#            credentials['OS_PASSWORD'] or os.environ['OS_PASSWORD'],
#            ex_tenant_name=credentials['OS_TENANT_NAME'],
#            ex_force_auth_url=credentials['OS_AUTH_URL'],
#            ex_force_auth_version=credentials['OS_VERSION'],
#            ex_force_service_region=credentials['OS_REGION_NAME']
#        )
