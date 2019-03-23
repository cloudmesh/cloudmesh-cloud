import os
import textwrap
import webbrowser
from pprint import pprint
from cloudmesh.common.Shell import Shell
from cloudmesh.common.dotdict import dotdict
# from cloudmesh.abstractclass import ComputeNodeManagerABC
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.console import Console
from cloudmesh.mongo import MongoDBController
from datetime import datetime

"""
is vagrant up to date

==> vagrant: A new version of Vagrant is available: 2.2.4 (installed version: 2.2.2)!
==> vagrant: To upgrade visit: https://www.vagrantup.com/downloads.html
"""


# noinspection PyUnusedLocal
class VboxProvider:

    def _check_version(self, r):
        """
        checks if vargarnt version is up to date

        :return:
        """
        return "A new version of Vagrant is available" not in r

    def __init__(self, cloud=None, config=None):

        self.config = Config()
        if cloud is None:
            cloud = self.config.cloud

        m = MongoDBController()
        status = m.status()
        if status.status == "error":
            raise Exception("ERROR: MongoDB is not running.")
        #
        # BUG: Naturally the following is wrong as it depends on the name.
        #
        # super().__init__("vagrant", config)

    def start(self, name):
        """
        start a node

        :param name: the unique node name
        :return:  The dict representing the node
        """
        pass

    def nodes(self, verbose=False):
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
            return data

        result = Shell.execute("vagrant", "global-status --prune")
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

    def boot(self, **kwargs):

        arg = dotdict(kwargs)
        arg.cwd = kwargs.get("cwd", None)

        # get the dir based on name

        print("ARG")
        pprint(arg)
        vms = self.to_dict(self.nodes())

        print("VMS", vms)

        arg = self._get_specification(**kwargs)

        pprint(arg)

        if arg.name in vms:
            Console.error("vm {name} already booted".format(**arg),
                          traceflag=False)
            return None

        else:
            self.create(**kwargs)
            Console.ok("{name} created".format(**arg))
            Console.ok("{directory}/{name} booting ...".format(**arg))

            result = Shell.execute("vagrant",
                                   ["up", arg.name],
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
        arg.path = config.data["cloudmesh"]["cloud"][cloud]["default"]["path"]
        arg.directory = os.path.expanduser("{path}/{name}".format(**arg))

        vms = self.to_dict(self.nodes())

        arg = "ssh {} -c {}".format(name, command)
        result = Shell.execute("vagrant", ["ssh", name, "-c", command],
                               cwd=arg.directory)
        return result

    def to_dict(self, lst, id="name"):

        d = {}
        if lst is not None:
            for entry in lst:
                d[entry[id]] = entry
        return d

    def stop(self, name=None):
        """
        stops the node with the given name

        :param name:
        :return: The dict representing the node including updated status
        """
        pass

    def _convert_assignment_to_dict(self, content):
        d = {}
        lines = content.split("\n")
        for line in lines:
            attribute, value = line.split("=", 1)
            attribute = attribute.replace('"', "")
            value = value.replace('"', "")

            d[attribute] = value
        return d

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
        arg.path = config.data["cloudmesh"]["cloud"][cloud]["default"]["path"]
        arg.directory = os.path.expanduser("{path}/{name}".format(**arg))

        data = {
            "cm": {
                "name": name,
                "directory": arg.directory,
                "path": arg.path,
                "cloud": cloud,
                "status": "unkown"
            }
        }
        result = None

        result = Shell.execute("vagrant",
                               ["ssh-config"],
                               cwd=arg.directory,
                               traceflag=False,
                               witherror=False)

        if result is None:
            data_vagrant = None
            data["cm"]["status"] = "poweroff"
        else:
            print(result)
            lines = result.split("\n")
            data_vagrant = {}
            for line in lines:
                attribute, value = line.strip().split(" ", 1)
                if attribute == "IdentityFile":
                    value = value.replace('"', '')

                data_vagrant[attribute] = value

        vms = Shell.execute('VBoxManage', ["list", "vms"]).split("\n")
        #
        # find vm
        #
        vbox_name_prefix = "{name}_{name}_".format(**arg)
        # print (vbox_name_prefix)
        details = None
        for vm in vms:
            vm = vm.replace("\"", "")
            vname = vm.split(" {")[0]
            if vname.startswith(vbox_name_prefix):
                details = Shell.execute("VBoxManage",
                                        ["showvminfo", "--machinereadable",
                                         vname])
                # print (details)
                break
        vbox_dict = self._convert_assignment_to_dict(details)

        # combined = {**data, **details}
        # data = combined
        if data_vagrant is not None:
            data["vagrant"] = data_vagrant
        data["vbox"] = vbox_dict
        if "VMState" in vbox_dict:
            data["cm"]["status"] = vbox_dict["VMState"]

        return data

    def suspend(self, name=None):
        """
        suspends the node with the given name

        :param name: the name of the node
        :return: The dict representing the node
        """
        # TODO: find last name if name is None
        result = Shell.execute("vagrant", ["suspend", name])
        return result

    def resume(self, name=None):
        """
        resume the named node

        :param name: the name of the node
        :return: the dict of the node
        """
        # TODO: find last name if name is None
        result = Shell.execute("vagrant", ["resume", name])
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
                               cwd=arg.directory)
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

    def _get_specification(self, cloud=None, name=None, port=None, image=None,
                           **kwargs):
        arg = dotdict(kwargs)
        arg.port = port
        config = Config()
        pprint(self.config)

        if cloud is None:
            #
            # TOD read default cloud
            #
            cloud = "vagrant"  # TODO must come through parameter or set cloud

        print("CCC", cloud)
        spec = config.data["cloudmesh"]["cloud"][cloud]
        pprint(spec)
        default = spec["default"]
        pprint(self.default)

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

    def create(self, name=None, image=None, size=None, timeout=360, port=80,
               **kwargs):
        """
        creates a named node

        :param port:
        :param name: the name of the node
        :param image: the image used
        :param size: the size of the image
        :param timeout: a timeout in seconds that is invoked in case the image does not boot.
               The default is set to 3 minutes.
        :param kwargs: additional arguments passed along at time of boot
        :return:
        """
        """
        create one node
        """

        #
        # TODO BUG: if name contains not just letters and numbers and - return error, e. undersore not allowed
        #

        arg = self._get_specification(name=name, image=image, size=size,
                                      timeout=timeout, port=port, **kwargs)

        if not os.path.exists(arg.directory):
            os.makedirs(arg.directory)

        configuration = self.vagrantfile(**arg)

        with open(arg.vagrantfile, 'w') as f:
            f.write(configuration)

        pprint(arg)

        return arg

    def rename(self, name=None, destination=None):
        """
        rename a node

        :param name: the current name
        :param destination: the new name
        :return: the dict with the new name
        """
        # if destination is None, increase the name counter and use the new name
        pass

    #
    # Additional methods
    #

    @classmethod
    def find_image(cls, keywords):
        """
        Finds an image on hashicorps web site

        :param keywords: The keywords to narrow down the search
        """
        d = {
            'key': '+'.join(keywords),
            'location': "https://app.vagrantup.com/boxes/search"
        }
        link = "{location}?utf8=%E2%9C%93&sort=downloads&provider=&q=\"{key}\"".format(
            **d)
        webbrowser.open(link, new=2, autoraise=True)

    #
    # ok. moved
    #
    @classmethod
    def list_images(cls):
        def convert(data_line):
            data_line = data_line.replace("(", "")
            data_line = data_line.replace(")", "")
            data_line = data_line.replace(",", "")
            data_entry = data_line.split(" ")
            data = dotdict()
            data.name = data_entry[0]
            data.provider = data_entry[1]
            data.date = data_entry[2]
            return data

        result = Shell.execute("vagrant", ["box", "list"])

        if "There are no installed boxes" in result:
            return None
        else:
            result = result.split("\n")
        lines = []
        for line in result:
            entry = convert(line)
            if "date" in entry:
                date = entry["date"]
                # "20181203.0.1"
                entry["date"] = datetime.strptime(date, '%Y%m%d.%H.%M')
            lines.append(entry)

        return lines
