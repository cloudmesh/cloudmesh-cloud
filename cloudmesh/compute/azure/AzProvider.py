from cloudmesh.common.Shell import Shell
import json
import webbrowser
from pprint import pprint

from cloudmesh.common.Shell import Shell
from cloudmesh.common.StopWatch import StopWatch


def timer(func):
    def decorated_func(*args, **kwargs):
        StopWatch.start(func.__name__)
        result = func(*args, **kwargs)
        StopWatch.stop(func.__name__)
        print(StopWatch.get(func.__name__))
        return result

    return decorated_func


class AzureProvider(object):
    """

    az commands

    https://docs.microsoft.com/en-us/cli/azure/reference-index?view=azure-cli-latest

    create the


    https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal


    """

    def __init__(self, resourcegroup=None):
        pass

    @timer
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
        r = self.az(f"az group delete --yes --name {name}")
        r = self.az(f"az group exists --name {name}")
        return r

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
        r = self.stop_vm(resource_group=resource_group, name=name)
        command = \
            "az vm delete --yes" \
                f" --resource-group {resource_group}" \
                f" --name {name}"
        return self.az(command)

    def list_vm(self,
                resource_group=None):
        try:
            command = \
                "az vm list " \
                    f" --resource-group {resource_group}"
            return self.az(command)
        except:
            return []

    def status_vm(self,
                  resource_group=None,
                  name=None):
        command = \
            "az vm get-instance-view" \
                f" --name {name}" \
                f" --resource-group {resource_group}" \
                f" --query instanceView.statuses[1]"
        return self.az(command)

    def stop_vm(self,
                resource_group=None,
                name=None):
        command = \
            f"az vm stop" \
                f" --resource-group {resource_group}" \
                f" --name {name}"
        return self.az(command)

    def start_vm(self,
                 resource_group=None,
                 name=None):
        command = \
            f"az vm start" \
                f" --resource-group {resource_group}" \
                f" --name {name}"
        # return self.az(command)
        print(command)
        r = Shell.execute(command, shell=True)

    def restart_vm(self,
                   resource_group=None,
                   name=None):
        command = \
            f"az vm restart" \
                f" --resource-group {resource_group}" \
                f" --name {name}"
        return self.az(command)

    def ssh_vm(self,
               user=None,
               command=None,
               resource_group=None,  # we need to get the ip not pass it
               name=None):
        ip = self.get_ip_vm(resource_group=resource_group, name=name)
        address = ip[0]['virtualMachine']['network']['publicIpAddresses'][0][
            'ipAddress']
        c = f'ssh -o "StrictHostKeyChecking no" {user}@{address} {command}'
        return Shell.execute(c, shell=True)

    def get_ip_vm(self,
                  resource_group=None,
                  name=None):
        command = f"az vm list-ip-addresses" \
            f" --resource-group {resource_group}" \
            f" --name {name}"
        return self.az(command)

        def connect_vm(self,
                       resource_group=None,
                       name=None,
                       user=None):
            print("connecting to vm...")
            ip = self.get_ip_vm(resource_group=resource_group, name=name)
            address = ip[0]['virtualMachine']['network']['publicIpAddresses'][0][
                'ipAddress']
            print(address)
            # command = f"ssh {user}@{address}"
            r = Shell.live("ssh {user}@{publicIdAddress}".format(user=user, \
                                                                 publicIdAddress=address))
            return r


if __name__ == "__main__":
    #
    # TODO: convert this to nsoetests
    #

    p = AzureProvider("test")
    # r = p.login()
    # pprint(r)

    # p.portal()

    name = "vm3"
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

    '''
    r = p.create_vm(resource_group=group,
                    name=name,
                    image="UbuntuLTS",
                    username="ubuntu")
    print(type(r))
    pprint(r)
    
    r = p.list_vm(resource_group=group)
    print(type(r))
    pprint(r)
    
    # az vm get-instance-view --name vm3 --resource-group test1 --query instanceView.statuses[1]
    
    r = p.status_vm(resource_group=group,
                    name=name)
    print(type(r))
    pprint(r)
    '''

    r = p.ssh_vm(
        user="ubuntu",
        resource_group=group,
        name=name,
        command="uname -a")

    print(r)

    '''
    r = p.delete_vm(resource_group=group,
                    name=name)
    
    print(type(r))
    pprint(r)
    
    r = p.list_vm(resource_group=group)
    print(type(r))
    pprint(r)
    '''
