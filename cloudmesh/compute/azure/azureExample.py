from cloudmesh.common.util import banner
from libcloud.compute.base import NodeAuthSSHKey
from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider

cls = get_driver(Provider.AZURE_ARM)
driver = cls(tenant_id='...',
             subscription_id='...',
             key='...',
             secret='...',
             region='centralus',
             )

auth = NodeAuthSSHKey('ssh-rsa ...')

banner('locations/regions')
locs = driver.list_locations()
print(locs)

banner('resource groups')
resgroups = driver.ex_list_resource_groups()
print(resgroups)

# resource group need to be created via azure portal
resgroup = 'cmtest'

banner('public IPs')
pubips = driver.ex_list_public_ips(resgroup)
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
for apub in publishers:
    print(apub[1])
    if apub[1] == publishername:
        publisherpath = apub[0]

banner('offers from a publisher - Canonical')
offers = driver.ex_list_offers(publisherpath)
offername = 'UbuntuServer'
offerpath = ''
for aoffer in offers:
    print(aoffer[1])
    if aoffer[1] == offername:
        offerpath = aoffer[0]

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
secgroups = driver.ex_list_network_security_groups(resgroup)
print(secgroups)

banner('List public IPs')
pubips = driver.ex_list_public_ips(resgroup)
print(pubips)

banner('create a public IP')
pubip = driver.ex_create_public_ip(name='pubip1',
                                   resource_group=resgroup
                                   )
print(pubip)

banner('List public IPs')
pubips = driver.ex_list_public_ips(resgroup)
print(pubips)

banner('nics')
nic = driver.ex_create_network_interface(name='cminternal',
                                         subnet=subnets[0],
                                         resource_group=resgroup,
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
                          ex_resource_group=resgroup,
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
