import getpass
import pprint
from cm4.vm.thread import Thread
from cm4.configuration.config import Config
from cm4.configuration.name import Name
from cm4.configuration.counter import Counter
from cm4.mongo.mongoDB import MongoDB
from cm4.vm.Azure import AzureProvider
from cm4.vm.Aws import AwsProvider
from cm4.openstack.OpenstackCM import OpenstackCM
from cm4.abstractclass.CloudManagerABC import CloudManagerABC


class Vm(CloudManagerABC):

    def __init__(self, cloud):
        self.mongo = MongoDB()
        self.config = Config().data["cloudmesh"]
        self.public_key_path = self.config["profile"]["key"]["public"]
        self.kind = self.config["cloud"][cloud]["cm"]["kind"]

        if self.kind == 'azure':
            self.provider = AzureProvider(self.config)
        elif self.kind == 'aws':
            self.provider = AwsProvider(self.config)
        elif self.kind == 'openstack':
            self.provider = OpenstackCM("chameleon")
        elif self.kind == 'vbox':
            raise NotImplementedError
        else:
            raise NotImplementedError(f"Cloud `{self.kind}` not supported.")

    def start(self, name):
        """
        start the node based on the id
        :param name:
        :return: VM document
        """
        if self.kind in ["vbox"]:
            raise NotImplementedError
        else:
            info = self.info(name)
            if info.state != 'running':
                self.provider.start(**info)

                Thread(self, 'test', name, 'running').start()
                document = self.mongo.find_document('cloud', 'name', name)
                return document
            else:
                document = self.mongo.find_document('cloud', 'name', name)
                return document

    def stop(self, name=None):
        """
        stop the node based on the ide
        :param name:
        :return: VM document
        """
        info = self.info(name)
        if info.state != 'stopped':
            self.provider.stop(name)
            Thread(self, 'test', name, 'stopped').start()
            document = self.mongo.find_document('cloud', 'name', name)
            return document
        else:
            document = self.mongo.find_document('cloud', 'name', name)
            return document

    def resume(self, name=None):
        """
        start the node based on id
        :param name:
        """
        return self.start(name)

    def suspend(self, name=None):
        """
        stop the node based on id
        :param name:
        """
        return self.stop(name)

    def destroy(self, name=None):
        """
        delete the node based on id
        :param name:
        :return: True/False
        """
        result = self.provider.destroy(name)
        self.mongo.delete_document('cloud', 'name', name)
        return result

    def create(self, name=None):
        """
        create a new node
        :param name: the name for the new node
        :return:
        """
        name = name or self.new_name()
        node = self.provider.create(name=name)
        self.mongo.insert_cloud_document(vars(node))
        Thread(self, 'test', name, 'running').start()
        return node

    def nodes(self):
        return self.provider.nodes()

    def status(self, name):
        """
        show node information based on id
        :param name:
        :return: all information about one node
        """
        self.info(name)
        status = self.mongo.find_document('cloud', 'name', name)['state']
        return status

    def info(self, name=None):
        """
        show node information based on id
        :param name:
        :return: all information about one node
        """
        nodes = self.nodes()
        for i in nodes:
            if i.name == name:
                document = vars(i)
                if self.mongo.find_document('cloud', 'name', name):
                    self.mongo.update_document('cloud', 'name', name, document)
                else:
                    self.mongo.insert_cloud_document(document)
                return i
        raise ValueError(f"Node: {name} does not exist!")

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


def process_arguments(arguments):
    """
    Process command line arguments to execute VM actions.
    Called from cm4.command.command
    :param arguments:
    """
    config = Config()
    default_cloud = config.data["cloudmesh"]["default"]["cloud"]
    vm = Vm(default_cloud)

    result = None

    if arguments.get("--debug"):
        pp = pprint.PrettyPrinter(indent=4)
        print("vm processing arguments")
        pp.pprint(arguments)
        # pp.pprint(config.data)

    if arguments.get("list"):
        result = vm.nodes()

    elif arguments.get("start"):
        try:
            result = vm.start(arguments.get("--vms"))
        except ValueError:
            vm_name = arguments.get("VMNAME")
            vm.create(vm_name)
            result = f"Created {vm_name}"

    elif arguments.get("stop"):
        result = vm.stop(arguments.get("--vms"))

    elif arguments.get("destroy"):
        result = vm.destroy(arguments.get("--vms"))

    elif arguments.get("status"):
        result = vm.status(arguments.get("--vms"))

    elif arguments.get("publicip"):
        result = vm.get_public_ips(arguments.get('--vms'))

    elif arguments.get("ssh"):
        # TODO
        raise NotImplementedError("cm4 vm ssh command has not yet been implemented")

    elif arguments.get("run"):
        # TODO
        raise NotImplementedError("cm4 vm run command has not yet been implemented")

    elif arguments.get("script"):
        # TODO
        raise NotImplementedError("cm4 vm script command has not yet been implemented")

    return result
