from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver


Openstack = get_driver(Provider.OPENSTACK)

con = Openstack(
    'admin', 'password',
    ex_force_base_url='cc@129.114.108.170',
    api_version='2.0',
    ex_tenant_name='demo')

cls = get_driver(Provider.OPENSTACK)
driver = cls('username', 'api key', region='iad')

sizes = driver.list_sizes()
images = driver.list_images()

size = [s for s in sizes if s.id == 'performance1-1'][0]
image = [i for i in images if 'Ubuntu 12.04' in i.name][0]

node = driver.create_node(name='libcloud', size=size, image=image)
print(node)












