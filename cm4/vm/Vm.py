from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver


class Provider(object):

    def __init__(self):
        config = Config()
        os_config = config.get("openstack")

    def get_driver(self, cloud):
        credential = self.os_config.get("credentials")

        Openstack = get_driver(Provider.OPENSTACK)
        driver = Openstack(
            credential.get('user'),
            credential.get('password'),
            ex_force_base_url=credential.get("url"),
            api_version=credential.get("api_version"),
            ex_tenant_name=credential.get("tennant_name"))
        return driver



class Vm(object):

    def __init__(self, cloud):
        self.provider = Provider (cloud)
        pass
           
    def start(self):
        pass
    
    def stop(self):
        pass
    
    def resume(self):
        pass
        
    def suspend(self):
        pass
        
    def destroy(self):
        pass
    
    def create(self):
        pass
    
    def listlike(self):
        pass
    
    def status(self):
        pass
    






