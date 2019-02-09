from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from config import Config


# TODO: BUG: Provider also in libcloud
class Provider(object):

    def __init__(self):
        config = Config()
        self.os_config = config.get_cloud().get("vm")

    def get_driver(self, cloud):
        credential = self.os_config.get("credentials")

        openstack = get_driver(Provider.OPENSTACK)
        driver = openstack(
            credential.get('user'),
            credential.get('password'),
            ex_force_base_url=credential.get("url"),
            api_version=credential.get("api_version"),
            ex_tenant_name=credential.get("tennant_name"))
        return driver


def connection_test():
    provider = Provider("chameleon")
    driver = provider.get_driver()

    sizes = driver.list_sizes()
    images = driver.list_images()

    size = [s for s in sizes if s.id == 'performance1-1'][0]
    image = [i for i in images if 'Ubuntu 12.04' in i.name][0]

    node = driver.create_node(name='libcloud', size=size, image=image)
    print(node)


# test running point
if __name__ == "__main__":
    connection_test()

# TODO
'''

class Vm(object):

    __init__(cloud)
       self.provider = Provider (cloud)
       
    
    start
    stop
    resume
    suspend
    destroy
    create
    list
    status
    ...
    
    
'''
