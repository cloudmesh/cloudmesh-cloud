import getpass
from cloudmesh.management.configuration.config import Config
from cloudmesh.management.configuration.name import Name
from cloudmesh.management.configuration.counter import Counter
from cloudmesh.mongo.mongoDB import MongoDB
from cloudmesh.vm.api.Azure import AzureProvider
from cloudmesh.vm.api.Aws import AwsProvider
from cloudmesh.openstack.OpenstackCM import OpenstackCM
from cloudmesh.abstractclass import ComputeNodeManagerABC
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
from cloudmesh.vbox.api.provider import VboxProvider

#
# if name is none, take last name from mongo, apply to last started vm
#


class Vm(ComputeNodeManagerABC):

    def __init__(self, cloud):
        self.mongo = MongoDB()
        self.config = Config().data["cloudmesh"]
        self.kind = self.config["cloud"][cloud]["cm"]["kind"]
        super().__init__(cloud, self.config)

        if self.kind == 'azure':
            self.provider = AzureProvider(self.config)
        elif self.kind == 'aws':
            self.provider = AwsProvider(self.config)
        elif self.kind == 'openstack':
            self.provider = OpenstackCM("chameleon")
        elif self.kind == "vbox":   # not sure about vbox vs vagrant in vbox provider
            self.provider = VboxProvider("vagrant")
        else:
            raise NotImplementedError(f"Cloud `{self.kind}` not supported.")

    @DatabaseUpdate("cloud", ComputeNodeManagerABC.map_default)
    def start(self, name):
        """
        start the node based on the id
        :param name:
        :return: VM document
        """
        info = self.info(name)
        if info["state"] != "running":
            info = self.provider.start(name)
        return info

    @DatabaseUpdate("cloud", ComputeNodeManagerABC.map_default)
    def stop(self, name=None):
        """
        stop the node based on the ide
        :param name:
        :return: VM document
        """
        return self.provider.stop(name)

    @DatabaseUpdate("cloud", ComputeNodeManagerABC.map_default)
    def resume(self, name=None):
        """
        start the node based on id
        :param name:
        """
        return self.start(name)

    @DatabaseUpdate("cloud", ComputeNodeManagerABC.map_default)
    def suspend(self, name=None):
        """
        stop the node based on id
        :param name:
        """
        return self.provider.suspend(name)

    @DatabaseUpdate("cloud", ComputeNodeManagerABC.map_default)
    def destroy(self, name=None):
        """
        delete the node based on id
        :param name:
        :return: True/False
        """
        result = self.provider.destroy(name)
        # self.mongo.delete_document('cloud', 'name', name)
        return result

    @DatabaseUpdate("cloud", ComputeNodeManagerABC.map_vm_create)
    def create(self, name=None):
        """
        create a new node
        :param name: the name for the new node
        :return:
        """
        name = name or self.new_name()
        return self.provider.create(name=name)

    @DatabaseUpdate("cloud", ComputeNodeManagerABC.map_default)
    def nodes(self):
        return self.provider.nodes()

    # @DatabaseUpdate("cloud", ComputeNodeManagerABC._map_default)
    def info(self, name=None):
        """
        show node information based on id

        TODO: seems like this should look in mongo, not self.nodes
            probably the solution is a more broad change to dynamically
            set the provider based on a name/cloud lookup in mongo.

        :param name:
        :return: all information about one node
        """
        return self.provider.info(name)

    def new_name(self, experiment=None, group=None, user=None):
        """
        Generate a VM name with the format `experiment-group-name-<counter>` where `counter`
        represents a running count of VMs created.

        Defaults can be modified in the cloudmesh4.yaml file.

        :param experiment:
        :param group:
        :param user:
        :return: The generated name.
        """
        experiment = experiment or self.config["default"]["experiment"]
        group = group or self.config["default"]["group"]
        user = user or getpass.getuser()

        counter = Counter()
        count = counter.get()
        name = Name()
        name_format = {'experiment': experiment, 'group': group, 'user': user, 'counter': count}
        name.set_schema('instance')
        counter.incr()
        return name.get(name_format)

    def get_public_ips(self, name=None):
        """
        Returns all the public ips available if a name is not given.
        If a name is provided, the ip of the vm name would be returned.
        :param name: name of the VM.
        :return: Dictionary of VMs with their public ips
        """
        if name is None:
            filters = {
                "$exists": True,
                "$not": {"$size": 0}
            }
            documents = self.mongo.find('cloud', 'public_ips', filters)
            if documents is None:
                return None
            else:
                result = {}
                for document in documents:
                    result[document['name']] = document['public_ips']
                return result
        else:
            public_ips = self.mongo.find_document('cloud', 'name', name)['public_ips']
            if not public_ips:
                return None
            else:
                return {name: public_ips}

    def set_public_ip(self, name, public_ip):
        """
        Assign the given public ip to the given VM.
        :param name: name of the VM
        :param public_ip: public ip to be assigned.
        """
        if name is not None and public_ip is not None:
            self.provider.set_public_ip(name, public_ip)

    def remove_public_ip(self, name):
        """
        Deletes the public ip of the given VM.
        :param name: name of the VM
        """
        if name is not None:
            self.provider.remove_public_ip(name)

