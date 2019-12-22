import os

from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.ssh.ssh_config import ssh_config
from cloudmesh.common.util import path_expand
from cloudmesh.common.variables import Variables
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.shell.command import PluginCommand, map_parameters
from cloudmesh.shell.command import command


# see https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/SecureShellCommand.py


class SshCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_ssh(self, args, arguments):
        """
        ::

            Usage:
                ssh
                ssh config list [--output=OUTPUT]
                ssh config add NAME IP [USER] [KEY]
                ssh config delete NAME
                ssh host delete NAME
                ssh host add NAME
                ssh [--name=VMs] [--user=USERs] [COMMAND]

            Arguments:
              NAME        Name or ip of the machine to log in
              list        Lists the machines that are registered and
                          the commands to login to them
              PARAMETERS  Register te resource and add the given
                          parameters to the ssh config file.  if the
                          resource exists, it will be overwritten. The
                          information will be written in /.ssh/config

            Options:
               -v                verbose mode
               --output=OUTPUT   the format in which this list is given
                                 formats includes cat, table, json, yaml,
                                 dict. If cat is used, it is just printed as
                                 is. [default: table]
               --user=USERs      overwrites the username that is
                                 specified in ~/.ssh/config
               --name=CMs        the names of the VMS to execute the
                                 command on

            Description:
                ssh config list
                    lists the hostsnames that are present in the
                    ~/.ssh/config file

                ssh config add NAME IP [USER] [KEY]
                    registers a host i ~/.ssh/config file
                    Parameters are attribute=value pairs
                    Note: Note yet implemented

                ssh [--name=VMs] [--user=USERs] [COMMAND]
                    executes the command on the named hosts. If user is
                    specified and is greater than 1, it must be specified for
                    each vm. If only one username is specified it is used for
                    all vms. However, as the user is typically specified in the
                    cloudmesh database, you probably do not have to specify
                    it as it is automatically found.

            Examples:


                 ssh config add blue 192.168.1.245 blue

                     Adds the following to the !/.ssh/config file

                     Host blue
                          HostName 192.168.1.245
                          User blue
                          IdentityFile ~/.ssh/id_rsa.pub



        """

        map_parameters(arguments,
                       "name",
                       "user",
                       "output")

        if arguments.config and arguments.list:
            # ssh config list [--output=OUTPUT]"

            hosts = dict(ssh_config().hosts)

            print(Printer.dict_table(hosts,
                                     order=['host', 'HostName', 'User',
                                            'IdentityFile']))

        elif arguments.config and arguments.add:
            # ssh config add NAME IP [USER] [KEY]

            variables = Variables()

            user = Parameter.find("user",
                                  arguments,
                                  variables.dict())

            key = Parameter.find("key",
                                 arguments,
                                 variables.dict(),
                                 {"key": "~/.ssh/id_rsa.pub"})

            name = arguments.NAME or variables['vm']

            ip = arguments.IP

            hosts = ssh_config()

            if name in hosts.hosts:
                Console.error("Host already in ~/.ssh/config")
                return ""

            hosts.generate(
                host=name,
                hostname=ip,
                identity=key,
                user=user)

        elif arguments.config and arguments.delete:
            # ssh config delete NAME

            raise NotImplementedError

        elif arguments.config and arguments.add:
            # ssh host add NAME

            location = path_expand("~/.ssh/known_hosts")
            name = arguments.NAME
            os.system("ssh-keygen -R {name}")
            os.system(f"ssh-keyscan -H {name} >> {location}")

        elif arguments.config and arguments.delete:
            # ssh host delete NAME

            name = arguments.NAME
            os.system("ssh-keygen -R {name}")

        elif (arguments.name and arguments.COMMAND) or arguments.COMMAND:
            # ssh [--name=VMs] [--user=USERs] [COMMAND]"

            variables = Variables()

            if arguments.name is None:
                name = arguments.NAME or variables['vm']
                names = [name]
            else:
                names = Parameter.expand(arguments.name)
            users = Parameter.expand(arguments.users)
            command = arguments.COMMAND

            if command is None and len(names) > 1:
                raise ValueError("For interactive shells the number of vms "
                                 "must be 1")
            elif command is None and len(names) == 1:

                # find the cloud

                cm = CmDatabase()
                vm = cm.find_name(names[0], kind="vm")[0]
                cloud = vm['cm']['cloud']

                # update the cloud
                provider = Provider(name=cloud)

                # update the vm
                provider.list()
                vm = cm.find_name(names[0], kind="vm")[0]

                # run ssh
                result = provider.ssh(vm=vm, command=command)
                print(result)
                return ""

            if len(names) > 1 and len(users) == 1:
                users = [users] * len(names)

            if len(names) > 1 and len(users) > 1 and len(names) != len(users):
                raise ValueError("vms and users have different length")

            for name in names:
                cm = CmDatabase()
                try:
                    vm = cm.find_name(name, kind="vm")[0]
                except IndexError:
                    Console.error(
                        "VM not found, make sure the vm exists in the list below: ")
                    os.system('cms vm list')
                    return

                cloud = vm['cm']['cloud']
                provider = Provider(name=cloud)
                result = provider.ssh(vm=vm, command=command)
                print(result)
        else:  # ssh with no argument
            last_vm = Variables()['vm']
            cm = CmDatabase()
            vm = cm.find_name(last_vm, kind="vm")[0]
            cloud = vm['cm']['cloud']
            provider = Provider(name=cloud)
            provider.ssh(vm=vm)
