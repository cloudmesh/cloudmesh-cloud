import getpass
from pprint  import pprint
from cm4.vm.Aws import Aws
from cm4.vm.Azure import Azure
from cm4.vm.Cmopenstack import Cmopenstack
from cm4.configuration.config import Config
from cm4.mongo.mongoDB import MongoDB
from cm4.configuration.name import Name
from cm4.vm.thread import Thread
from cm4.configuration.counter import Counter
from cm4.abstractclass.CloudManagerABC import CloudManagerABC
import cm4

class Vmprovider(object):

    def __init__(self):
        self.config = Config().data["cloudmesh"]

    def get_provider(self, cloud):
        """
        Create the driver based on the 'kind' information.
        This method could deal with AWS, AZURE, and OPENSTACK for CLOUD block of YAML file.
        Only developed for AZURE, AWS, Chameleon, but we haven't test OPENSTACK
        :return: the driver based on the 'kind' information
        """
        driver = None
        os_config = self.config["cloud"][cloud]

        if os_config.get('cm').get('kind') == 'azure':

            driver = cm4.vm.Azure.Azure()
            driver = Azure(self.config, cloud).driver
        elif os_config.get('cm').get('kind') == 'aws':
            driver = Aws(self.config, cloud).driver
        elif os_config.get('cm').get('kind') == 'openstack':
            driver = Cmopenstack(self.config, cloud).driver
        elif os_config.get('cm').get('kind') == 'vbox':
            driver = None
            raise NotImplementedError
        return driver


class Vm(CloudManagerABC):

    def __init__(self, cloud):
        self.mongo = MongoDB()
        self.config = Config().data["cloudmesh"]
        self.kind = self.config["cloud"][cloud]["kind"]
        if self.kind in ["vbox"]:
            raise NotImplementedError
            self.provider = None # ?????
        else:
            self.provider = Vmprovider().get_provider(cloud)


    def start(self, name):
        """
        start the node based on the id
        :param name:
        :return: VM document
        """
        if self.kind in ["vbox"]:
            raise NotImplementedError
            self.provider
        else:
            info = self.info(name)
            if info.state != 'running':
                #self.provider.ex_start_node(info)

                parameters = {
                    "name": "node1"
                }
                self.provider.start(**parameters)

                Thread(self, 'test', name, 'running').start()
                document = self.mongo.find_document('cloud', 'name', name)
                return document
            else:
                document = self.mongo.find_document('cloud', 'name', name)
                return document

    def stop(self, name, deallocate=True):
        """
        stop the node based on the ide
        :param name:
        :param deallocate:
        :return: VM document
        """
        info = self.info(name)
        if info.state != 'stopped':
            #
            # BUG: THIS SHOUDL NOT CALL LIBCLOUD BUT ONLY OUR OWN ABSTRACTIONS, IF CONDITION NEEDED
            #
            self.provider.ex_stop_node(info, deallocate)
            Thread(self, 'test', name, 'stopped').start()
            document = self.mongo.find_document('cloud', 'name', name)
            return document
        else:
            document = self.mongo.find_document('cloud', 'name', name)
            return document

    def resume(self, name):
        """
        start the node based on id
        :param name:
        """
        return self.start(name)

    def suspend(self, name):
        """
        stop the node based on id
        :param name:
        """
        return self.stop(name, False)

    def destroy(self, name):
        """
        delete the node based on id
        :param name:
        :return: True/False
        """
        result = self.provider.destroy_node(self.info(name))
        self.mongo.delete_document('cloud', 'name', name)
        return result

    def create(self, name=None):
        """
        create a new node
        :param name: the name for the new node
        :return:
        """
        name = name or self.new_name()
        node = self.provider.create_node(name)
        self.mongo.insert_cloud_document(vars(node))
        Thread(self, 'test', name, 'running').start()
        return node

    def list(self):
        """
        list existed nodes
        :return: all nodes' information
        """
        result = self.provider.list_nodes()
        return result

    def status(self, name):
        """
        show node information based on id
        :param name:
        :return: all information about one node
        """
        self.info(name)
        status = self.mongo.find_document('cloud', 'name', name)['state']
        return status

    def info(self, name):
        """
        show node information based on id
        :param name:
        :return: all information about one node
        """
        nodes = self.list()
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
    result = None

    if arguments.get("--debug"):
        pp = pprint.PrettyPrinter(indent=4)
        print("vm processing arguments")
        pp.pprint(arguments)
    config = Config()
    pprint(config.data)
    default_cloud = config.data["cloudmesh"]["default"]["cloud"]

    vm = Vm(default_cloud)

    if arguments.get("list"):
        result = vm.list()

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
        pass

    elif arguments.get("run"):
        # TODO
        pass

    elif arguments.get("script"):
        # TODO
        pass

    return result
