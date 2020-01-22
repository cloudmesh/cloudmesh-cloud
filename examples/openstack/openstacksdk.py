from openstack import connection
from pprint import pprint
import yaml
from cloudmesh.configuration.Config import Config
from cloudmesh.common.util import banner
import sys

cred = """
# This is a clouds.yaml file, which can be used by OpenStack tools as a source
# of configuration on how to connect to a cloud. If this is your only cloud,
# just put this file in ~/.config/openstack/clouds.yaml and tools like
# python-openstackclient will just work with no further config. (You will need
# to add your password to the auth section)
# If you have more than one cloud account, add the cloud entry to the clouds
# section of your existing file and you can refer to them by name with
# OS_CLOUD=openstack or --os-cloud=openstack
clouds:
  openstack:
    auth:
      auth_url: https://kvm.tacc.chameleoncloud.org:5000/v3
      username: TBD
      project_id: TB
      project_name: "cloudmesh"
      user_domain_name: "Default"
      password: 'TBD'
    region_name: "KVM@TACC"
    interface: "public"
    identity_api_version: 3
"""

#data = yaml.load(cred)['clouds']['openstack']
config = Config()
data = config['cloudmesh.cloud.chameleon.credentials']
pprint (data)

#with open(r'E:\data\fruits.yaml') as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
#    fruits_list = yaml.load(file, Loader=yaml.FullLoader)


conn = connection.Connection(**data)

banner("Connection")
print (conn)

servers = conn.list_servers()

pprint (servers[0]['hostname'])


#projects = conn.identity.projects()
#
#pprint(projects)
#for project in projects:
#    pprint(project)


banner("List Networks")

for network in conn.network.networks():
    pprint(network)

banner("List SubNetworks")


for subnet in conn.network.subnets():
    pprint(subnet)

banner("List Ports")

for port in conn.network.ports():
    pprint(port)


banner("List Routers")

for router in conn.network.routers():
    pprint(router)

print("List Network Agents")

for agent in conn.network.agents():
    pprint(agent)


banner("List Servers")

for server in conn.compute.servers():
    print(server)

banner("List Images")

for image in conn.compute.images():
    pprint(image)

banner("List Flavors:")

for flavor in conn.compute.flavors():
    pprint(flavor)


banner("List Security Groups")

for port in conn.network.security_groups():
    pprint(port)



    banner("Open a port:")

example_sec_group = conn.network.find_security_group(
    name_or_id='openstacksdk-example-security-group')



print(example_sec_group)

example_rule = conn.network.create_security_group_rule(
    security_group_id=example_sec_group.id,
    direction='ingress',
    remote_ip_prefix='0.0.0.0/0',
    protocol='tcp',
    port_range_max='5000',
    port_range_min='5000',
    ethertype='IPv4')

print(example_rule)



sys.exit()

print("Create Server:")

NAME="test2"
IMAGE="CC-Ubuntu18.04"
FLAVOR="m1.medium"
NETWORK="cloudmesh-net"
image = conn.compute.find_image(IMAGE)
flavor = conn.compute.find_flavor(FLAVOR)
network = conn.network.find_network(NETWORK)


data = {
    'description': f'cloudmesh-server-{NAME}',
    'name': NAME,
    'image_id': image.id,
    'flavor_id': flavor.id,
    'networks': [{"uuid": network.id}],
    'key_name': "gregor"
}

pprint (data)

server = conn.compute.create_server(
    name=NAME,
    image_id=image.id,
    flavor_id=flavor.id,
    networks=[{"uuid": network.id}],
    key_name="gregor")

server = conn.compute.wait_for_server(
    server,
    interval=10,
)

ip = server.access_ipv4

print(f"ssh -i id_rsa cc@{ip}")
