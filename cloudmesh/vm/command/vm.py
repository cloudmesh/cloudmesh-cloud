from __future__ import print_function

from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.variables import Variables
from cloudmesh.common.console import Console
from pprint import pprint
from cloudmesh.common.parameter import Parameter
from cloudmesh.management.configuration.config import Active

class VmCommand(PluginCommand):

    # see also https://github.com/cloudmesh/client/edit/master/cloudmesh_client/shell/plugins/VmCommand.py

    # noinspection PyUnusedLocal
    @command
    def do_vm(self, args, arguments):
        """
        ::

            Usage:
                vm ping [NAMES] [N]
                vm refresh [all] [--cloud=CLOUDS]
                vm start [NAMES]
                         [--experiment=EXPERIMENT]
                         [--group=GROUP]
                         [--cloud=CLOUD]
                         [--force]
                vm boot [--name=NAME]
                        [--cloud=CLOUD]
                        [--username=USERNAME]
                        [--image=IMAGE]
                        [--flavor=FLAVOR]
                        [--group=GROUP]
                        [--public]
                        [--secgroup=SECGROUP]
                        [--key=KEY]
                        [--dryrun]
                vm boot [--n=COUNT]
                        [--cloud=CLOUD]
                        [--username=USERNAME]
                        [--image=IMAGE]
                        [--flavor=FLAVOR]
                        [--group=GROUP]
                        [--public]
                        [--secgroup=SECGROUP]
                        [--key=KEY]
                        [--dryrun]
                vm run [--name=NAMES] [--username=USERNAME] COMMAND
                vm script [--name=NAMES] [--username=USERNAME] SCRIPT
                vm console [NAME]
                         [--group=GROUP]
                         [--cloud=CLOUD]
                         [--force]
                vm stop [NAMES]
                        [--group=GROUP]
                        [--cloud=CLOUD]
                        [--force]
                vm terminate [NAMES]
                          [--group=GROUP]
                          [--cloud=CLOUD]
                          [--force]
                vm delete [NAMES]
                          [--group=GROUP]
                          [--cloud=CLOUD]
                          [--keep]
                          [--dryrun]
                vm ip assign [NAMES]
                          [--cloud=CLOUD]
                vm ip show [NAMES]
                           [--group=GROUP]
                           [--cloud=CLOUD]
                           [--format=FORMAT]
                           [--refresh]
                vm ip inventory [NAMES]
                                [--header=HEADER]
                                [--file=FILE]
                vm ssh [NAME] [--username=USER]
                         [--quiet]
                         [--ip=IP]
                         [--cloud=CLOUD]
                         [--key=KEY]
                         [--command=COMMAND]
                         [--modify-knownhosts]
                vm rename [OLDNAMES] [NEWNAMES] [--force] [--dryrun]
                vm list [NAMES]
                        [--cloud=CLOUDS|--active]
                        [--group=GROUP]
                        [--format=FORMAT]
                        [--refresh]
                vm status [NAMES]
                vm wait [--cloud=CLOUD] [--interval=SECONDS]
                vm info [--cloud=CLOUD]
                        [--format=FORMAT]
                vm check NAME
                vm username USERNAME [NAMES] [--cloud=CLOUD]
                vm resize [SIZE]

            Arguments:
                COMMAND        positional arguments, the commands you want to
                               execute on the server(e.g. ls -a) separated by ';',
                               you will get a return of executing result instead of login to
                               the server, note that type in -- is suggested before
                               you input the commands
                NAME           server name. By default it is set to the name of last vm from database.
                NAMES          server name. By default it is set to the name of last vm from database.
                KEYPAIR_NAME   Name of the openstack keypair to be used to create VM. Note this is
                               not a path to key.
                NEWNAMES       New names of the VM while renaming.
                OLDNAMES       Old names of the VM while renaming.

            Options:
              -H --modify-knownhosts  Do not modify ~/.ssh/known_hosts file when ssh'ing into a machine
                --username=USERNAME  the username to login into the vm. If not specified it will be guessed
                                     from the image name and the cloud
                --ip=IP          give the public ip of the server
                --cloud=CLOUD    give a cloud to work on, if not given, selected
                                 or default cloud will be used
                --count=COUNT    give the number of servers to start
                --detail         for table print format, a brief version
                                 is used as default, use this flag to print
                                 detailed table
                --flavor=FLAVOR  give the name or id of the flavor
                --group=GROUP          give the group name of server
                --secgroup=SECGROUP    security group name for the server
                --image=IMAGE    give the name or id of the image
                --key=KEY        specify a key to use, input a string which
                                 is the full path to the private key file
                --keypair_name=KEYPAIR_NAME   Name of the openstack keypair to be used to create VM.
                                              Note this is not a path to key.
                --user=USER      give the user name of the server that you want
                                 to use to login
                --name=NAME      give the name of the virtual machine
                --force          rename/ delete vms without user's confirmation
                --command=COMMAND
                                 specify the commands to be executed


            Description:
                commands used to boot, start or delete servers of a cloud

                vm default [options...]
                    Displays default parameters that are set for vm boot either on the
                    default cloud or the specified cloud.

                vm boot [options...]
                    Boots servers on a cloud, user may specify flavor, image .etc, otherwise default values
                    will be used, see how to set default values of a cloud: cloud help

                vm start [options...]
                    Starts a suspended or stopped vm instance.

                vm stop [options...]
                    Stops a vm instance .

                vm delete [options...]
                    Delete servers of a cloud, user may delete a server by its name or id, delete servers
                    of a group or servers of a cloud, give prefix and/or range to find servers by their names.
                    Or user may specify more options to narrow the search

                vm floating_ip_assign [options...]
                    assign a public ip to a VM of a cloud

                vm ip show [options...]
                    show the ips of VMs

                vm ssh [options...]
                    login to a server or execute commands on it

                vm list [options...]
                    same as command "list vm", please refer to it

                vm status [options...]
                    Retrieves status of last VM booted on cloud and displays it.

            Tip:
                give the VM name, but in a hostlist style, which is very
                convenient when you need a range of VMs e.g. sample[1-3]
                => ['sample1', 'sample2', 'sample3']
                sample[1-3,18] => ['sample1', 'sample2', 'sample3', 'sample18']

            Quoting commands:
                cm vm login gvonlasz-004 --command=\"uname -a\"
        """

        def get_clouds(arguments, variables):
            clouds = arguments["--cloud"] or variables["cloud"]
            if clouds is None:
                Console.error("you need to specify a cloud")
                return None
            else:
                return Parameter.expand(clouds)

        """
        m = Manager()


        if arguments.FILE:
            print("option a")
            m.list(arguments.FILE)

        elif arguments.list:
            print("option b")
            m.list("just calling list without parameter")
        """

        pprint(arguments)

        variables = Variables()


        if arguments.refresh:

            clouds = None

            if arguments.all:

                Console.msg("refresh all active clouds")

                active = Active()
                clouds = active.clouds()

            else:

                clouds = get_clouds(arguments, variables)

            for cloud in clouds:
                Console.msg ("refresh {cloud}".format(cloud=cloud))
                # r = vm.refresh(cloud)
            return

        elif arguments.ping:

            names = Parameter.expand(arguments["NAMES"] or variables["vm"])
            pings = arguments["N"] or 3

            print (names)
            if names is None:
                Console.error("you need to specify a vm")
                return None
            else:
                for name in names:
                    Console.msg("ping {name}".format(name=name))
                    # r = vm.ping(name)

        elif arguments.boot:

            print("boot the vm")

        elif arguments.start:

            print("start the vm")

        elif arguments.stop:

            print("start the vm")

        elif arguments.delete:

            print("delete the vm")

        elif arguments.list:

            print("list the vms")

        elif arguments.rename:

            print("rename the vm")

        elif arguments["ip"] and arguments["show"]:

            print("show the ips")

        elif arguments["ip"] and arguments["assign"]:

            print("assign the public ip")

        elif arguments["ip"] and arguments["inventory"]:

            print("list ips that could be assigned")

        elif arguments.username:

            print("sets the username for the vm")

        elif arguments.default:

            print("sets defaults for the vm")

        elif arguments.ssh:

            print("ssh  the vm")


        elif arguments.console:

            print("console for the vm")

        elif arguments.status:

            print("status for the vm")

        elif arguments.info:

            print("info for the vm")

        elif arguments.wait:

            print("waits for the vm till its ready and one can login")

        elif arguments.wait:

            print("waits for the vm till its ready and one can login")
