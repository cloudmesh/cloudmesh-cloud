from cloudmesh.common.util import banner
from libcloud.compute.base import NodeAuthSSHKey
from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider

#
# This example is wrong as it should use Config()
#
# IT SETS A VERY WRONG EXAMPLE OF HARD CODING CREDENTIALS
#


cls = get_driver(Provider.AZURE_ARM)
#
# TODO: This needs to read from yaml with the Config()
#
driver = cls(tenant_id='...',
             subscription_id='...',
             key='...',
             secret='...',
             region='eastus',
             )

auth = NodeAuthSSHKey('ssh-rsa ...')

banner('locations/regions')
locations = driver.list_locations()
print(locations)

banner('resource groups')
groups = driver.ex_list_resource_groups()
print(groups)

# resource group need to be created via azure portal
group = 'cmtest'

banner('public IPs')
pubips = driver.ex_list_public_ips(group)
print(pubips)

banner('node sizes (list first 10)')
sizes = driver.list_sizes()
print(sizes[:10])

banner('images')
# images = driver.list_images()
# print (images[:10])
print("...too long to retrieve and load all images")

banner('image publishers')
publishers = driver.ex_list_publishers()
publishername = 'Canonical'
publisherpath = ''
for publisher in publishers:
    print(publisher[1])
    if publisher[1] == publishername:
        publisherpath = publisher[0]

banner('offers from a publisher - Canonical')
offers = driver.ex_list_offers(publisherpath)
offername = 'UbuntuServer'
offerpath = ''
for offer in offers:
    print(offer[1])
    if offer[1] == offername:
        offerpath = offer[0]

banner('skus from an offer - UbuntuServer')
skus = driver.ex_list_skus(offerpath)
skuname = '18.04-LTS'
skupath = ''
for asku in skus:
    print(asku[1])
    if asku[1] == skuname:
        skupath = asku[0]

banner('Images filtered by publisher, offer, and sku')
images = driver.list_images(ex_publisher=publishername,
                            ex_offer=offername,
                            ex_sku=skuname,
                            )
print(images)

# network and subnet need to be created once
# in the azure portal
# similar to what need to be done in openstack
# before the first use
#
banner('networks')
networks = driver.ex_list_networks()
print(networks)

banner('subnets')
subnets = driver.ex_list_subnets(networks[0])
print(subnets)

banner('nics')
nics = driver.ex_list_nics()
print(nics)

banner('security groups')
secgroups = driver.ex_list_network_security_groups(group)
print(secgroups)

banner('List public IPs')
pubips = driver.ex_list_public_ips(group)
print(pubips)

banner('create a public IP')
pubip = driver.ex_create_public_ip(name='pubip1',
                                   resource_group=group
                                   )
print(pubip)

banner('List public IPs')
pubips = driver.ex_list_public_ips(group)
print(pubips)

banner('nics')
nic = driver.ex_create_network_interface(name='cminternal',
                                         subnet=subnets[0],
                                         resource_group=group,
                                         public_ip=pubip
                                         )
nics = driver.ex_list_nics()
print(nics)

sizeid = 'Standard_B1s'
imageid = 'Canonical:UbuntuServer:18.04-LTS:18.04.201903200'

size = [s for s in sizes if s.id == sizeid][0]
image = driver.get_image(imageid)

banner('node creation')
node = driver.create_node(name="fwpytest",
                          size=size,
                          image=image,
                          auth=auth,
                          # the following three were created in azure portal
                          ex_resource_group=group,
                          # for storage account, use the default v2 setting
                          ex_storage_account='cmtestfw',
                          # under the storage account, blobs services, 
                          # create 'vhds' container
                          ex_blob_container='vhds',
                          ex_nic=nic,
                          )
print(node)

banner('nodes')
nodes = driver.list_nodes()
print(nodes)
