import os
import platform
import shlex
import subprocess
import sys
import textwrap
import webbrowser
from pprint import pprint

from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.util import path_expand
# from cloudmesh.abstractclass import ComputeNodeManagerABC
from cloudmesh.configuration.Config import Config

"""
is vagrant up to date

==> vagrant: A new version of Vagrant is available: 2.2.4 (installed version: 2.2.2)!
==> vagrant: To upgrade visit: https://www.vagrantup.com/downloads.html
"""


class Provider(ComputeNodeABC):
    kind = "virtualbox"

    def run_command(self, command):
        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
        while True:
            output = process.stdout.read(1)
            if output == b'' and process.poll() is not None:
                break
            if output:
                sys.stdout.write(output.decode("utf-8"))
                sys.stdout.flush()
        rc = process.poll()
        return rc

    def update_dict(self, entry, kind="node"):
        if "cm" not in entry:
            entry["cm"] = {}
        entry["cm"]["kind"] = kind
        entry["cm"]["driver"] = self.cloudtype
        entry["cm"]["cloud"] = self.cloud
        return entry

    output = {
        'vm': {
            "sort_keys": ["cm.name"],
            'order': ["vagrant.name",
                      "vagrant.cloud",
                      "vbox.name",
                      "vagrant.id",
                      "vagrant.provider",
                      "vagrant.state",
                      "vagrant.hostname"],
            'header': ["Name",
                       "Cloud",
                       "Vbox",
                       "Id",
                       "Provider",
                       "State",
                       "Hostname"]
        },
        'image': None,
        'flavor': None
    }

    def __init__(self, name=None,
                 configuration="~/.cloudmesh/.cloudmesh.yaml"):
        self.config = Config()
        conf = Config(configuration)["cloudmesh"]
        self.user = conf["profile"]
        self.spec = conf["cloud"][name]
        self.cloud = name
        cred = self.spec["credentials"]
        self.cloudtype = self.spec["cm"]["kind"]

        if platform.system().lower() == "darwin":
            self.vboxmanage = \
                "/Applications/VirtualBox.app/Contents/MacOS/VBoxManage"
        else:
            self.vboxmanage = "VBoxManage"

        # m = MongoDBController()
        # status = m.status()
        # if status.status == "error":
        #    raise Exception("ERROR: MongoDB is not running.")
        #
        # BUG: Naturally the following is wrong as it depends on the name.
        #
        # super().__init__("vagrant", config)

    # noinspection PyPep8
    def version(self):
        """
        This command returns the versions ov vagrant and virtual box
        :return: A dict with the information

        Description:

          The output looks like this

          {'vagrant': '2.2.4',
           'virtualbox': {'extension': {
                            'description': 'USB 2.0 and USB 3.0 Host '
                                           'Controller, Host Webcam, '
                                           'VirtualBox RDP, PXE ROM, Disk '
                                           'Encryption, NVMe.',
                              'extensionpack': True,
                              'revision': '128413',
                              'usable': 'true',
                              'version': '6.0.4'},
                'version': '6.0.4'}}

        """

        version = {
            "vagrant": None,
            "virtualbox": {
                "version": None,
                "extension": None
            }
        }

        try:
            result = Shell.execute("vagrant --version", shell=True)
            txt, version["vagrant"] = result.split(" ")

            if "A new version of Vagrant is available" in result:
                Console.error(
                    "Vagrant is outdated. Please download a new version of "
                    "vagrant")
                raise NotImplementedError
        except:
            pass

        try:

            result = Shell.execute(self.vboxmanage, shell=True)
            txt, version["virtualbox"]["version"] = result.split("\n")[0].split(
                "Version ")

            result = Shell.execute(self.vboxmanage + " list -l extpacks",
                                   shell=True)
            extension = {}

            for line in result.split("\n"):
                if "Oracle VM VirtualBox Extension Pack" in line:
                    extension["extensionpack"] = True
                elif "Revision:" in line:
                    extension["revision"] = line.split(":")[1].strip()
                elif "Usable:" in line:
                    extension["usable"] = line.split(":")[1].strip()
                elif "Description:" in line:
                    extension["description"] = line.split(":")[1].strip()
                elif "Version:" in line:
                    extension["version"] = line.split(":")[1].strip()

            version["virtualbox"]["extension"] = extension

        except:
            pass

        return version

    def images(self):
        def convert(data_line):
            data_line = data_line.replace("(", ",")
            data_line = data_line.replace(")", ",")
            data_entry = data_line.split(",")
            data = dotdict()
            data.name = data_entry[0].strip()
            data.provider = data_entry[1].strip()
            data.version = data_entry[2].strip()
            data = self.update_dict(data, kind="image")
            return data

        result = Shell.execute("vagrant box list", shell=True)

        if "There are no installed boxes" in result:
            return None
        else:
            result = result.split("\n")
        lines = []
        for line in result:
            entry = convert(line)
            if "date" in entry:
                date = entry["date"]
            lines.append(entry)

        return lines

    def delete_image(self, name=None):
        result = ""
        if name is None:
            pass
            return "ERROR: please specify an image name"
            # read name form config
        else:
            try:
                command = "vagrant box remove {name}".format(name=name)
                result = Shell.execute(command, shell=True)
            except Exception as e:
                print(e)

            return result

    def add_image(self, name=None):

        command = "vagrant box add {name} --provider virtualbox".format(
            name=name)

        result = ""
        if name is None:
            pass
            return "ERROR: please specify an image name"
            # read name form config
        else:
            try:
                command = "vagrant box add {name} --provider virtualbox".format(
                    name=name)
                result = Shell.live(command)
                assert result.status == 0
            except Exception as e:
                print(e)
                print(result)
                print()

            return result

    def _check_version(self, r):
        """
        checks if vagrant version is up to date

        :return:
        """
        return "A new version of Vagrant is available" not in r

    def start(self, name):
        """
        start a node

        :param name: the unique node name
        :return:  The dict representing the node
        """
        pass

    def vagrant_nodes(self, verbose=False):
        """
        list all nodes id

        :return: an array of dicts representing the nodes
        """

        def convert(data_line):

            entry = (' '.join(data_line.split())).split(' ')
            data = dotdict()
            data.id = entry[0]
            data.name = entry[1]
            data.provider = entry[2]
            data.state = entry[3]
            data.directory = entry[4]
            data = self.update_dict(data, kind="node")
            return data

        result = Shell.execute("vagrant global-status --prune", shell=True)
        if verbose:
            print(result)
        if "There are no active" in result:
            return None

        lines = []
        for line in result.split("\n")[2:]:
            if line == " ":
                break
            else:
                lines.append(convert(line))
        return lines

    def create(self, **kwargs):

        arg = dotdict(kwargs)
        arg.cwd = kwargs.get("cwd", None)

        # get the dir based on name

        print("ARG")
        pprint(arg)
        vms = self.to_dict(self.vagrant_nodes())

        print("VMS", vms)

        arg = self._get_specification(**kwargs)

        pprint(arg)

        if arg.name in vms:
            Console.error("vm {name} already booted".format(**arg),
                          traceflag=False)
            return None

        else:
            self.create_spec(**kwargs)
            Console.ok("{name} created".format(**arg))
            Console.ok("{directory}/{name} booting ...".format(**arg))

            result = None
            result = Shell.live("vagrant up " + arg.name,
                                cwd=arg.directory)
            Console.ok("{name} ok.".format(**arg))

            return result

    def execute(self, name, command, cwd=None):

        arg = dotdict()
        arg.cwd = cwd
        arg.command = command
        arg.name = name
        config = Config()
        cloud = "vagrant"  # TODO: must come through parameter or set cloud
        arg.path = config.data["cloudmesh"]["cloud"][cloud]["default"][
            "path"]
        arg.directory = os.path.expanduser("{path}/{name}".format(**arg))

        vms = self.to_dict(self.vagrant_nodes())

        arg = "ssh {} -c {}".format(name, command)
        result = Shell.execute("vagrant", ["ssh", name, "-c", command],
                               cwd=arg.directory,
                               shell=True)
        return result

    def to_dict(self, lst, id="name"):

        d = {}
        if lst is not None:
            for entry in lst:
                d[entry[id]] = entry
        return d

    def _convert_assignment_to_dict(self, content):
        d = {}
        lines = content.split("\n")
        for line in lines:
            attribute, value = line.split("=", 1)
            attribute = attribute.replace('"', "")
            attribute = attribute.replace(' ', "_")
            attribute = attribute.replace('-', "_")
            attribute = attribute.replace('-', "_")
            attribute = attribute.replace('/', "_")
            attribute = attribute.replace(')', "")
            attribute = attribute.replace('(', "-")
            attribute = attribute.replace(']', "")
            attribute = attribute.replace('[', "_")

            value = value.replace('"', "")

            d[attribute] = value
        return d

    def find(self, nodes=None, name=None):
        if nodes is None:
            nodes = self.vagrant_nodes()
        pprint(nodes)
        if name in nodes:
            return nodes[name]
        return None

    def info(self, name=None):
        """
        gets the information of a node with a given name

        :param name:
        :return: The dict representing the node including updated status
        """

        arg = dotdict()
        arg.name = name

        config = Config()

        cloud = "vagrant"  # TODO: must come through parameter or set cloud
        arg.path = config.data["cloudmesh"]["cloud"][cloud]["default"][
            "path"]
        arg.directory = os.path.expanduser("{path}/{name}".format(**arg))

        result = None

        vms = Shell.execute(self.vboxmanage + " list vms", shell=True).replace(
            '"', '').replace('{', '').replace('}', '').split("\n")
        vagrant_data = self.to_dict(self.vagrant_nodes())

        data = {}
        for entry in vagrant_data:
            data[entry] = {
                "vagrant": vagrant_data[entry]
            }

        for line in vms:
            vbox_name, id = line.split(" ")
            vagrant_name = vbox_name.split("_")[0]

            data[vagrant_name]["name"] = vagrant_name
            data[vagrant_name]["vbox_name"] = vbox_name

            data[vagrant_name]["id"] = id

        vms = data

        #
        # find vm
        #
        vbox_name_prefix = "{name}_{name}_".format(**arg)
        # print (vbox_name_prefix)
        details = None
        for vm in vms:
            vbox_name = vms[vm]["vbox_name"]

            details = Shell.execute(
                self.vboxmanage + " showvminfo --machinereadable " + vbox_name,
                shell=True)
            data[vm]["vbox"] = self._convert_assignment_to_dict(details)

        for vm in data:
            directory = path_expand(
                "~/.cloudmesh/vagrant/{name}".format(name=vm))

            data[vm]["cm"] = {
                "name": vm,
                "directory": arg.directory,
                "path": arg.path,
                "cloud": cloud,
                "status": data[vm]["vagrant"]['state']
            }
            data[vm] = self.update_dict(data[vm], kind="node")

            result = Shell.execute("vagrant ssh-config",
                                   cwd=directory,
                                   traceflag=False,
                                   witherror=False,
                                   shell=True)
            if result is not None:
                lines = result.split("\n")
                for line in lines:
                    attribute, value = line.strip().split(" ")
                    attribute = attribute.lower()
                    data[vm]['vagrant'][attribute] = value

        if name is not None:
            return data[name]

        result = []
        for d in data:
            print(d)
            result.append(data[d])
        return result

    def suspend(self, name=None):
        """
        NOT IMPLEMENTED

        suspends the node with the given name

        :param name: the name of the node
        :return: The dict representing the node
        """
        # TODO: find last name if name is None

        arg = dotdict()
        arg.name = name

        # TODO find the vbx name from vagrantname

        arg.path = self.default["path"]
        arg.directory = os.path.expanduser("{path}/{name}".format(**arg))

        result = Shell.execute("vbox", ["suspend", name], cwd=arg.directory,
                               shell=True)
        return result

    def resume(self, name=None):
        """
        NOT IMPLEMENTED

        Default: resume(start) all the VMs specified.
        If @name is provided, only the named VM is started.

        :param name: [optional], name of the Vagrant VM.
        :return:
        """
        # TODO: find last name if name is None

        arg = dotdict()
        arg.name = name

        # TODO find the vbx name from vagrantname

        arg.path = self.default["path"]
        arg.directory = os.path.expanduser("{path}/{name}".format(**arg))

        result = Shell.execute("vbox", ["up", name], cwd=arg.directory,
                               shell=True)
        return result

    def resume(self, name=None):
        """
        resume the named node

        :param name: the name of the node
        :return: the dict of the node
        """
        # TODO: find last name if name is None
        result = Shell.execute("vagrant", ["resume", name], shell=True)
        return result

    def stop(self, name=None):
        """
        NOT IMPLEMENTED

        stops the node with the given name

        :param name: the name of the node
        :return: The dict representing the node
        """
        # TODO: find last name if name is None

        arg = dotdict()
        arg.name = name

        # TODO find the vbx name from vagrantname

        arg.path = self.default["path"]
        arg.directory = os.path.expanduser("{path}/{name}".format(**arg))

        result = Shell.execute("vbox", ["stop", name], cwd=arg.directory,
                               shell=True)
        return result

    def destroy(self, name=None):
        """
        Destroys the node
        :param name: the name of the node
        :return: the dict of the node
        """
        self.delete(name=name)

    # @classmethod
    def delete(self, name=None):
        # TODO: check

        arg = dotdict()
        arg.name = name
        arg.path = self.default["path"]
        arg.directory = os.path.expanduser("{path}/{name}".format(**arg))

        result = Shell.execute("vagrant",
                               ["destroy", "-f", name],
                               cwd=arg.directory, shell=True)
        return result

    def vagrantfile(self, **kwargs):

        arg = dotdict(kwargs)

        provision = kwargs.get("script", None)

        if provision is not None:
            arg.provision = 'config.vm.provision "shell", inline: <<-SHELL\n'
            for line in textwrap.dedent(provision).split("\n"):
                if line.strip() != "":
                    arg.provision += 12 * " " + "    " + line + "\n"
            arg.provision += 12 * " " + "  " + "SHELL\n"
        else:
            arg.provision = ""

        # not sure how I2 gets found TODO verify, comment bellow is not enough
        # the 12 is derived from the indentation of Vagrant in the script
        # TODO we may need not just port 80 to forward
        script = textwrap.dedent("""
               Vagrant.configure(2) do |config|

                 config.vm.define "{name}"
                 config.vm.hostname = "{name}"
                 config.vm.box = "{image}"
                 config.vm.box_check_update = true
                 config.vm.network "forwarded_port", guest: 80, host: {port}
                 config.vm.network "private_network", type: "dhcp"

                 # config.vm.network "public_network"
                 # config.vm.synced_folder "../data", "/vagrant_data"
                 config.vm.provider "virtualbox" do |vb|
                    # vb.gui = true
                    vb.memory = "{memory}"
                 end
                 {provision}
               end
           """.format(**arg))

        return script

    def _get_specification(self, cloud=None, name=None, port=None,
                           image=None, **kwargs):
        arg = dotdict(kwargs)
        arg.port = port
        config = Config()
        pprint(self.config)

        if cloud is None:
            #
            # TOD read default cloud
            #
            cloud = "vagrant"  # TODO must come through parameter or set cloud

        spec = config.data["cloudmesh"]["cloud"][cloud]
        default = spec["default"]
        pprint(default)

        if name is not None:
            arg.name = name
        else:
            # TODO get new name
            pass

        if image is not None:
            arg.image = image
        else:
            arg.image = default["image"]
            pass

        arg.path = default["path"]
        arg.directory = os.path.expanduser("{path}/{name}".format(**arg))
        arg.vagrantfile = "{directory}/Vagrantfile".format(**arg)
        return arg

    def create_spec(self, name=None, image=None, size=1024, timeout=360,
                    port=80,
                    **kwargs):
        """
        creates a named node

        :param port:
        :param name: the name of the node
        :param image: the image used
        :param size: the size of the image
        :param timeout: a timeout in seconds that is invoked in case the image
                        does not boot. The default is set to 3 minutes.
        :param kwargs: additional arguments passed along at time of boot
        :return:
        """
        """
        create one node
        """

        #
        # TODO BUG: if name contains not just letters and numbers and -
        #  return error, e. underscore not allowed
        #

        arg = self._get_specification(name=name,
                                      image=image,
                                      size=size,
                                      memory=size,
                                      timeout=timeout,
                                      port=port,
                                      **kwargs)

        if not os.path.exists(arg.directory):
            os.makedirs(arg.directory)

        configuration = self.vagrantfile(**arg)

        with open(arg.vagrantfile, 'w') as f:
            f.write(configuration)

        pprint(arg)

        return arg

    #
    # Additional methods
    #

    @classmethod
    def find_image(cls, keywords):
        """
        Finds an image on hashicorps web site

        :param keywords: The keywords to narrow down the search
        """

        key = '+'.join(keywords)
        location = "https://app.vagrantup.com/boxes/search"
        link = \
            f"{location}?utf8=%E2%9C%93&sort=downloads&provider=&q=\"{key}\""

        webbrowser.open(link, new=2, autoraise=True)

    def list(self, raw=True):
        """
        list all nodes id
    
        :return: an array of dicts representing the nodes
        """
        result = None
        if raw:
            result = self.info()
        else:
            result = self.vagrant_nodes()
        return result

    def rename(self, name=None, destination=None):
        """
        rename a node
    
        :param destination:
        :param name: the current name
        :return: the dict with the new name
        """

        arguments = ['modifyvm', '"', name, '"', "--name", '"', destination,
                     '"']

        vms = Shell.execute(self.vboxmanage, arguments, shell=True).split("\n")
        return {}

    def list_os(self):
        """
        :return: the dict with the new name
        """

        result = Shell.execute(self.vboxmanage + " list ostypes", shell=True)

        data = {}

        result = result.split("\n\n")
        entries = {}

        id = "None"
        for element in result:
            attributes = element.split("\n")
            for a in attributes:

                attribute, value = a.split(":")
                value = value.strip()
                attribute = attribute.lower()
                attribute = attribute.replace(" ", "_")
                print(">>>>", attribute, value)
                if attribute == "id":
                    id = value
                    entries[id] = {}
                entries[id][attribute] = value

        return entries

    def key_upload(self, key):
        raise NotImplementedError
