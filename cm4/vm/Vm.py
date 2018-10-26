from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver


class Provider(object):

    def __init__(self):
        config = Config()
        os_config = config.get("openstack")
    
    def get(self, cloud):
        if self.osconfig["cm]["type"]  == "openstack": # ????
          credential = os[config][credentials]  
          openstack = get_driver(Provider.OPENSTACK)


        con = Openstack(
        config["user"], 
        config{'password'],
        ex_force_base_url=config["url"]
        api_version=config["api_versiom],
        ex_tenant_name=config["tennant_name"])

        cls = get_driver(Provider.RACKSPACE)
        driver = cls('username', 'api key', region='iad')


        return driver

class Vm(object):

    __init__(cloud)
       self.provider = Provider (cloud)
           
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
    
    

"""    
    
provider = Provider("chameleon")


sizes = driver.list_sizes()
images = driver.list_images()

size = [s for s in sizes if s.id == 'performance1-1'][0]
image = [i for i in images if 'Ubuntu 12.04' in i.name][0]

node = driver.create_node(name='libcloud', size=size, image=image)
print(node)


    

"""







