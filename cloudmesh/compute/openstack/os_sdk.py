#
# python cloudmesh/compute/openstack/os_sdk.py
#

from cloudmesh.management.configuration.config import Config
from pprint import pprint
import openstack


"""
see : https://docs.openstack.org/openstacksdk/latest/user/guides/compute.html
"""

"""
cloudmesh4.yaml file
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
    # while libcloud uses token, here we do not use it in auth_url
    d['auth_url'] = config['OS_AUTH_URL'].replace("/tokens","")
    d['project_id'] = config['OS_TENANT_NAME']
    d['region_name'] = config['OS_REGION_NAME']
    # d['project_domain_name'] = config['OS_PROJECT_NAME']
    d['tenant_id'] = config['OS_TENANT_ID']
    return d

config = credentials()

pprint(config)

connection = openstack.connect(**config)
cloud = connection.compute

if False:
    flavors = cloud.flavors()
    for entry in flavors:
        pprint(entry)

if False:
    images = cloud.images()
    for entry in images:
        pprint(entry)

if True:
    servers = cloud.servers()
    for entry in servers:
        pprint(entry)

