from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

# tg837909
# Lee091120115!

Openstack = get_driver(Provider.OPENSTACK)

con = Openstack(
    'admin', 'password',
    ex_force_base_url='http://23.12.198.36:8774/v2.1',
    api_version='2.0',
    ex_tenant_name='demo')

cls = get_driver(Provider.RACKSPACE)
driver = cls('username', 'api key', region='iad')

sizes = driver.list_sizes()
images = driver.list_images()

size = [s for s in sizes if s.id == 'performance1-1'][0]
image = [i for i in images if 'Ubuntu 12.04' in i.name][0]

node = driver.create_node(name='libcloud', size=size, image=image)
print(node)












