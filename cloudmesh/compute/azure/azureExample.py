from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from libcloud.compute.drivers.azure_arm import AzureNodeDriver
from libcloud.compute.base import NodeAuthSSHKey

cls = get_driver(Provider.AZURE_ARM)
driver = cls(tenant_id='...',
             subscription_id='...',
             key='...',
             secret='...',
             region='centralus',
             )

auth = NodeAuthSSHKey('ssh-rsa ...')

print ("%s%s%s" % ('*'*30, 'locations/regions', '*'*30))
locs = driver.list_locations()
print (locs)

print ("%s%s%s" % ('*'*30, 'resource groups', '*'*30))
resgroups = driver.ex_list_resource_groups()
print (resgroups)

# resource group need to be created via azure portal
resgroup = 'cmtest'

print ("%s%s%s" % ('*'*30, 'public IPs', '*'*30))
pubips = driver.ex_list_public_ips(resgroup)
print (pubips)

print ("%s%s%s" % ('*'*30, 'node sizes (list first 10)', '*'*30))
sizes = driver.list_sizes()
print (sizes[:10])

print ("%s%s%s" % ('*'*30, 'images', '*'*30))
#images = driver.list_images()
#print (images[:10])
print ("...too long to retrieve and load all images")

print ("%s%s%s" % ('-'*20, 'image publishers', '-'*20))
publishers = driver.ex_list_publishers()
publishername = 'Canonical'
publisherpath = ''
for apub in publishers:
    print (apub[1])
    if apub[1] == publishername:
        publisherpath = apub[0]

print ("%s%s%s" % ('-'*20, 'offers from a publisher - Canonical', '-'*20))
offers = driver.ex_list_offers(publisherpath)
offername = 'UbuntuServer'
offerpath = ''
for aoffer in offers:
    print (aoffer[1])
    if aoffer[1] == offername:
        offerpath = aoffer[0]

print ("%s%s%s" % ('-'*20, 'skus from an offer - UbuntuServer', '-'*20))
skus = driver.ex_list_skus(offerpath)
skuname = '18.04-LTS'
skupath = ''
for asku in skus:
    print (asku[1])
    if asku[1] == skuname:
        skupath = asku[0]

print ("%s%s%s" % ('='*20, 'Images filtered by publisher, offer, and sku', '='*20))
images = driver.list_images(ex_publisher=publishername,
                            ex_offer=offername,
                            ex_sku=skuname,
                            )
print (images)

# network and subnet need to be created once
# in the azure portal
# similar to what need to be done in openstack
# before the first use
#
print ("%s%s%s" % ('*'*30, 'networks', '*'*30))
networks = driver.ex_list_networks()
print (networks)

print ("%s%s%s" % ('*'*30, 'subnets', '*'*30))
subnets = driver.ex_list_subnets(networks[0])
print (subnets)

print ("%s%s%s" % ('*'*30, 'nics', '*'*30))
nics = driver.ex_list_nics()
print (nics)

print ("%s%s%s" % ('*'*30, 'security groups', '*'*30))
secgroups = driver.ex_list_network_security_groups(resgroup)
print (secgroups)

print ("%s%s%s" % ('*'*30, 'List public IPs', '*'*30))
pubips = driver.ex_list_public_ips(resgroup)
print (pubips)

print ("%s%s%s" % ('*'*30, 'create a public IP', '*'*30))
pubip = driver.ex_create_public_ip(name='pubip1',
                                   resource_group=resgroup
                                   )
print (pubip)

print ("%s%s%s" % ('*'*30, 'List public IPs', '*'*30))
pubips = driver.ex_list_public_ips(resgroup)
print (pubips)

print ("%s%s%s" % ('*'*30, 'nics', '*'*30))
nic = driver.ex_create_network_interface(name='cminternal',
                                         subnet=subnets[0],
                                         resource_group=resgroup,
                                         public_ip=pubip
                                        )
nics = driver.ex_list_nics()
print (nics)

sizeid = 'Standard_B1s'
imageid = 'Canonical:UbuntuServer:18.04-LTS:18.04.201903200'

size = [s for s in sizes if s.id == sizeid][0]
image = driver.get_image(imageid)

print ("%s%s%s" % ('*'*30, 'node creation', '*'*30))
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
print (node)

print ("%s%s%s" % ('*'*30, 'nodes', '*'*30))
nodes = driver.list_nodes()
print (nodes)

