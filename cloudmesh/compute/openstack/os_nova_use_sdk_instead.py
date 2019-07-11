from cloudmesh.management.configuration.config import Config
from novaclient.client import Client
from keystoneauth1 import session
from glanceclient import Client
from glanceclient import Client as ImageClient
from pprint import pprint

"""
        OS_AUTH_URL: https://openstack.tacc.chameleoncloud.org:5000/v2.0/tokens
        OS_USERNAME: TBD
        OS_PASSWORD: TBD
        OS_TENANT_NAME: CH-819337
        OS_TENANT_ID: CH-819337
        OS_PROJECT_NAME: CH-819337
        OS_PROJECT_DOMAIN_ID: default
        OS_USER_DOMAIN_ID: default
        OS_VERSION: liberty
        OS_REGION_NAME: RegionOne
        OS_KEY_PATH: ~/.ssh/id_rsa.pub
"""

def credentials():
    d = {}

    config = Config()["cloudmesh.cloud.chameleon.credentials"]
    d['version'] = '2'
    d['username'] = config['OS_USERNAME']
    d['password'] = config['OS_PASSWORD']
    d['auth_url'] = "https://openstack.tacc.chameleoncloud.org:5000/v2.0"
    d['project_id'] = config['OS_TENANT_NAME']
    d['region_name'] = config['OS_REGION_NAME']
    # d['project_domain_name'] = config['OS_PROJECT_NAME']
    d['tenant_id'] = config['OS_TENANT_ID']
    return d

config = credentials()

pprint(config)

#nova_client = Client(**config,
#                     connection_pool=True)

#flavors = nova_client.flavors.list()
#for entry in flavors:
#    pprint(entry.__dict__)


#servers = nova_client.servers.list()
#for entry in servers:
#    pprint(entry.__dict__)


#pprint (dir(nova_client))

glance_client = ImageClient(**config)

#images = nova_client.images.GlanceManager.list()
#or entry in images:
#    pprint(entry.__dict__)


#print(nova_client.servers.list())
