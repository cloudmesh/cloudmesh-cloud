from __future__ import print_function
from cloudmesh_client.common.Shell import Shell
from cloudmesh_client.common.dotdict import dotdict
import textwrap
import os
from cloudmesh_client.shell.console import Console
from pprint import pprint


class vm(object):
    @classmethod
    def create(cls, **kwargs):

        arg = dotdict(kwargs)

        if not os.path.exists(arg.name):
            os.makedirs(arg.name)

        config = cls.vagrantfile(**kwargs)

        with open('{name}/Vagrantfile'.format(**arg), 'w') as f:
            f.write(config)

    @classmethod
    def vagrantfile(cls, **kwargs):

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



        # the 12 is derived from the indentation of Vagrant in the script
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

    @classmethod
    def info(cls, name=None):
        result = Shell.execute("vagrant",
                               ["ssh-config"],
                               cwd=name)
        lines = result.split("\n")
        data = {}
        for line in lines:
            attribute, value = line.strip().split(" ", 1)
            if attribute == "IdentityFile":
                value = value.replace('"','')

            data[attribute] = value
        return data

    @classmethod
    def list(cls, verbose=False):

        def convert(line):
            entry = (' '.join(line.split())).split(' ')
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

    @classmethod
    def delete(cls, name=None):

        result = Shell.execute("vagrant",
                               ["destroy", "-f", name],
                               cwd=name)
        return result

    @classmethod
    def boot(cls, **kwargs):

        arg = dotdict(kwargs)
        arg.cwd = kwargs.get("cwd", None)

        vms = cls.to_dict(cls.list())

        if arg.name in vms:
            Console.error("vm {name} already booted".format(**arg), traceflag=False)
            return None
        # print result

        else:
            cls.create(**kwargs)
            Console.ok("{name} created".format(**arg))
            Console.ok("{name} booting ...".format(**arg))

            result = Shell.execute("vagrant",
                                   ["up", arg.name],
                                   cwd=arg.name)
            Console.ok("{name} ok.".format(**arg))

            return result

    @classmethod
    def resume(cls, name):
        result = Shell.execute("vagrant", ["resume", name])
        return result

    @classmethod
    def suspend(cls, name):
        result = Shell.execute("vagrant", ["suspend", name])
        return result

    @classmethod
    def execute(cls, name, command, cwd=None):

        vms = cls.to_dict(cls.list())

        arg = "ssh {} -c {}".format(name, command)
        result = Shell.execute("vagrant", ["ssh", name, "-c", command], cwd=vms[name]["directory"])
        return result

    @classmethod
    def to_dict(cls, lst, id="name"):
        d = {}
        for entry in lst:
            d[entry[id]] = entry
        return d
