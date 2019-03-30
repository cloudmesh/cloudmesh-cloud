from azure.mgmt.resource import ResourceManagementClient
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.Shell import Shell
from pprint import pprint
import webbrowser
import json
import textwrap
from cloudmesh.compute.libcloud.Provider import Provider
from cloudmesh.common.dotdict import dotdict




class AzureProvider(object):
    """

    az commands

    https://docs.microsoft.com/en-us/cli/azure/reference-index?view=azure-cli-latest

    create the


    https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal


    """

    def __init__(self, resourcegroup=None):
        pass

    def az(self, command):
        print(command)
        r = Shell.execute(command, shell=True)
        data = json.loads(r)
        return data

    def login(self):
        r = Shell.execute("az login", shell=True)
        r = r.replace("true", "True")
        r = eval("[\n" + r.split("[")[1])
        return r

    def portal(self):
        webbrowser.open("https://portal.azure.com")

    def create_resource_group(self, name=None, location=None):
        if name is None or location is None:
            raise ValueError(
                f"Reosurce can not be found, Name: {name}, Location: {location}")
        return self.az(f"az group create --name {name} --location {location}")

    def delete_resource_group(self, name=None):
        if name is None:
            raise ValueError(f"Reosurce can not be found, Name: {name}")
        r = Shell.execute(f"az group delete --yes --name {name}", shell=True)
        r = Shell.execute(f"az group exists --name {name}", shell=True)
        data = json.loads(r)
        return data

    def list_resource_group(self):
        return self.az("az group list")

    def create_vm(self,
                  resource_group=None,
                  name=None,
                  image=None,
                  username=None):
        # first check if vm exists, if it does return error
        command = \
            "az vm create" \
                f" --resource-group {resource_group}" \
                f" --name {name}" \
                f" --image {image}" \
                f" --admin-username {username}" \
                f" --generate-ssh-keys"

        return self.az(command)

    def delete_vm(self,
                  resource_group=None,
                  name=None):
        command = \
            "az vm delete --yes" \
                f" --resource-group {resource_group}" \
                f" --name {name}"
        return self.az(command)

    def list_vm(self,
                resource_group=None):
        command = \
            "az vm list " \
                f" --resource-group {resource_group}"
        return self.az(command)


p = AzureProvider("test")
# r = p.login()
# pprint(r)

# p.portal()

group = "test1"
location = "eastus"
# r = p.create_resource_group(name=group, location=location)
# print(type(r))
# pprint(r)
# r = p.delete_resource_group(name=group)
# print(type(r))
# pprint(r)

r = p.list_vm(resource_group=group)
print(type(r))
pprint(r)

r = p.create_vm(resource_group=group,
                name="vm01",
                image="UbuntuLTS",
                username="ubuntu")
print(type(r))
pprint(r)

r = p.list_vm(resource_group=group)
print(type(r))
pprint(r)

r = p.delete_vm(resource_group=group,
                name="vm01")

print(type(r))
pprint(r)

r = p.list_vm(resource_group=group)
print(type(r))
pprint(r)
