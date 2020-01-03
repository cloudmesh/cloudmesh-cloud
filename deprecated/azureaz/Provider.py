import json
import webbrowser
from pprint import pprint

from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.common.Shell import Shell
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import path_expand
from cloudmesh.configuration.Config import Config


def timer(func):
    def decorated_func(*args, **kwargs):
        StopWatch.start(func.__name__)
        result = func(*args, **kwargs)
        StopWatch.stop(func.__name__)
        print(StopWatch.get(func.__name__))
        return result

    return decorated_func


class Provider(ComputeNodeABC):
    """

    az commands

    https://docs.microsoft.com/en-us/cli/azure/reference-index?view=azure-cli-latest

    create the


    https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal


    """

    kind = "azureaz"

    """
    # THIS NEED STO BE DEFINED ONCE WE SEE THE OUTPUT
    
    output = {

        "vm": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.cloud",
                      "state",
                      "image",
                      "public_ips",
                      "private_ips",
                      "cm.kind"],
            "header": ["cm.name",
                       "cm.cloud",
                       "state",
                       "image",
                       "public_ips",
                       "private_ips",
                       "cm.kind"]
        },
        "image": {"sort_keys": ["cm.name",
                                "extra.minDisk"],
                  "order": ["cm.name",
                            "extra.minDisk",
                            "updated",
                            "cm.driver"],
                  "header": ["Name",
                             "MinDisk",
                             "Updated",
                             "Driver"]},
        "flavor": {"sort_keys": ["cm.name",
                                 "vcpus",
                                 "disk"],
                   "order": ["cm.name",
                             "vcpus",
                             "ram",
                             "disk"],
                   "header": ["Name",
                              "VCPUS",
                              "RAM",
                              "Disk"]}

    }
    """

    def __init__(self, name=None, configuration="~/.cloudmesh/cloudmesh.yaml"):
        configuration = path_expand(configuration)
        conf = Config(name, configuration)["cloudmesh"]

        super().__init__(name, configuration)
        self.user = conf["profile"]["user"]
        self.spec = conf["cloud"][name]
        self.cloud = name
        cred = self.spec["credentials"]
        deft = self.spec["default"]
        self.cloudtype = self.spec["cm"]["kind"]
        self.resource_group = cred["resourcegroup"]
        self.credentials = cred

    def update_dict(self, entry, kind="node"):
        if "cm" not in entry:
            entry["cm"] = {}
        entry["cm"]["kind"] = kind
        entry["cm"]["driver"] = self.cloudtype
        entry["cm"]["cloud"] = self.cloud
        entry["cm"]["name"] = entry["name"]
        return entry

    def update_list(self, data):
        for entry in data:
            data = self.update_dict(entry)
        return data

    @timer
    def az(self, command):
        print(command)
        r = Shell.execute(command, shell=True)
        data = json.loads(r)
        if command.startswith('az vm create'):
            data['id'] = None
        if command.startswith('az vm list --resource-group'):
            data[0]['id'] = None
            data[0]['networkProfile']['networkInterfaces'][0]['id'] = None
            data[0]['storageProfile']['osDisk']['managedDisk']['id'] = None
        if command.startswith('az vm list-ip-addresses'):
            data[0]['virtualMachine']['network']['publicIpAddresses'][0][
                'id'] = None
        pprint(data)
        return data

    def az_2(self, command):
        print(command)
        r = Shell.live(command)
        return r

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
                f"Resource can not be found, "
                "Name: {name}, Location: {location}")
        return self.az(f"az group create --name {name} --location {location}")

    def delete_resource_group(self, name=None):
        if name is None:
            raise ValueError(f"Resource can not be found, Name: {name}")
        r = self.az(f"az group delete --yes --name {name}")
        r = self.az(f"az group exists --name {name}")
        return r

    def list_resource_group(self):
        return self.az("az group list")

    def create(self, name=None, image=None, size=None, timeout=360, **kwargs):
        username = kwargs["username"]

        # first check if vm exists, if it does return error
        # noinspection PyPep8
        command = \
            "az vm create" \
            f" --resource-group {self.resource_group}" \
            f" --name {name}" \
            f" --image {image}" \
            f" --admin-username {username}" \
            f" --generate-ssh-keys"

        return self.az(command)

    def destroy(self, name=None):
        r = self.stop(name=name)
        # noinspection PyPep8
        command = \
            "az vm delete --yes" \
            f" --resource-group {self.resource_group}" \
            f" --name {name}"
        # print(command)
        # r = Shell.execute(command, shell=True)
        # BUG MUST RETURN A DICT
        return self.az_2(command)

    # noinspection PyPep8
    def list(self):
        try:
            # noinspection PyPep8
            command = \
                "az vm list" \
                f" --resource-group {self.resource_group}"
            data = self.az(command)
            data = self.update_list(data)
            VERBOSE(data)
            return data
        except:
            return []

    def info(self, name=None):
        command = f"az vm show" \
                  f" --resource-group {self.resource_group}" \
                  f" --name {name}"
        return self.az(command)

    def status(self, name=None):
        # noinspection PyPep8
        command = \
            "az vm get-instance-view" \
            f" --name {name}" \
            f" --resource-group {self.resource_group}" \
            f" --query instanceView.statuses[1]"
        return self.az(command)

    def stop(self, name=None):
        # noinspection PyPep8
        command = \
            f"az vm stop" \
            f" --resource-group {self.resource_group}" \
            f" --name {name}"
        # print(command)
        # r = Shell.execute(command, shell=True)
        return self.az_2(command)

    def start(self, name=None):
        # noinspection PyPep8
        command = \
            f"az vm start" \
            f" --resource-group {self.resource_group}" \
            f" --name {name}"
        # return self.az(command)
        # print(command)
        # r = Shell.execute(command, shell=True)
        # MUST BE RETURNING A DICT
        return self.az_2(command)

    def restart(self,
                name=None):
        # noinspection PyPep8
        command = \
            f"az vm restart" \
            f" --resource-group {self.resource_group}" \
            f" --name {name}"
        return self.az(command)

    def ssh(self,
            user=None,
            command=None,
            name=None):
        ip = self.get_ip(name=name)
        address = ip[0]['virtualMachine']['network']['publicIpAddresses'][0][
            'ipAddress']
        c = f'ssh -o "StrictHostKeyChecking no" {user}@{address} {command}'
        return Shell.execute(c, shell=True)

    def get_ip(self,

               name=None):
        command = f"az vm list-ip-addresses" \
                  f" --resource-group {self.resource_group}" \
                  f" --name {name}"
        return self.az(command)

    def connect(self,

                name=None,
                user=None):
        print("connecting to vm...")
        ip = self.get_ip(name=name)
        address = ip[0]['virtualMachine']['network']['publicIpAddresses'][0][
            'ipAddress']
        print(address)
        # command = f"ssh {user}@{address}"
        command = "ssh {user}@{publicIdAddress}".format(user=user,
                                                        publicIdAddress=address)
        return self.az_2(command)

    def list_image(self,
                   location=None):
        # noinspection PyPep8
        command = \
            "az vm image list" \
            f" --location {location}"
        # THIS OUGHT TO RETURN A DICT
        return self.az_2(command)

    def list_size(self,
                  location=None):
        # noinspection PyPep8
        command = \
            "az vm list-sizes" \
            f" --location {location}"
        # THIS SHOULD RETURN A DICT
        return self.az_2(command)

    def connect_to_all(self):
        vm_list = self.list()
        for i in range(len(vm_list)):
            vm_name = vm_list[i]['name']
            username = vm_list[i]['osProfile']['adminUsername']
            self.wait_orig(self.resource_group, vm_name, username)

    # noinspection PyPep8
    def wait_orig(self,

                  vm_name=None,
                  username=None,
                  time=10):
        re_try = 5
        print("connecting to: {}".format(vm_name))
        try:
            r = self.connect(
                name=vm_name,
                user=username)
        except:
            for i in range(re_try):
                time.sleep(
                    120)  # wait for two minutes before re-try to connect
                result = self.connect(self,

                                      name=vm_name, user=username)
                if result:
                    break

    def rename(self, name=None, destination=None):
        raise NotImplementedError
        # RETURN A DICT

    def resume(self, name=None):
        raise NotImplementedError
        # THIS SHOULD RETURN A DICT

    def suspend(self, name=None):
        raise NotImplementedError
        # THIS SHOULD RETURN A DICT


if __name__ == "__main__":
    p = Provider("test")
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

    r = p.list()
    print(type(r))
    pprint(r)

    '''
    r = p.create(
                    name=name,
                    image="UbuntuLTS",
                    username="ubuntu")
    print(type(r))
    pprint(r)
    
    r = p.list()
    print(type(r))
    pprint(r)
    
    # az vm get-instance-view --name vm3 --resource-group test1 \
    #                         --query instanceView.statuses[1]
    
    r = p.status(
                    name=name)
    print(type(r))
    pprint(r)
    '''

    r = p.ssh(
        user="ubuntu",
        name=name,
        command="uname -a")

    print(r)

    '''
    r = p.delete(
                    name=name)
    
    print(type(r))
    pprint(r)
    
    r = p.list()
    print(type(r))
    pprint(r)
    '''
