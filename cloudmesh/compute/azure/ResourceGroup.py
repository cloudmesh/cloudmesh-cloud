from azure.mgmt.resource import ResourceManagementClient
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.Shell import Shell
from pprint import pprint
import webbrowser
import json
import textwrap
from cloudmesh.compute.libcloud.Provider import Provider


class AzureProvider(object):
    """
    create the


    https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal


    """

    def __init__(self, resourcegroup=None):
        pass

    def login(self):
        r = Shell.execute("az login", shell=True)
        r = r.replace("true", "True")
        r = eval("[\n" + r.split("[")[1])
        return r

    def portal(self):
        webbrowser.open("https://portal.azure.com")

    def list_resourcegroup(self):
        p = Provider("azure")

        # cls = get_driver(Provider.AZURE_ARM)
        # driver = cls(tenant_id='...',
        #             subscription_id='...',
        #             key='...',
        #             secret='...',
        #             region='centralus',
        #             )

        # print("%s%s%s" % ('*' * 30, 'resource groups', '*' * 30))
        # resgroups = driver.ex_list_resource_groups()
        # print(resgroups)

        pass


# p = AzureProvider("test")
# r = p.login()
# pprint(r)

p.portal()

# LOCATION = 'eastus'
# GROUP_NAME ='sample_resource_group'


# resource_client = ResourceManagementClient(credentials, subscription_id)
# resource_client.resource_groups.create_or_update(GROUP_NAME, {'location': LOCATION})
