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
                vm ping [NAMES] [--cloud=CLOUDS] [N]
                vm check [NAMES] [--cloud=CLOUDS]
                vm refresh [NAMES] [--cloud=CLOUDS]
                vm status [NAMES] [--cloud=CLOUDS]
                vm console [NAME] [--force]
                vm start [NAMES] [--cloud=CLOUD] [--dryrun]
                vm stop [NAMES] [--cloud=CLOUD] [--dryrun]
                vm terminate [NAMES] [--cloud=CLOUD] [--dryrun]
                vm delete [NAMES] [--cloud=CLOUD] [--dryrun]
                vm list [NAMES]
                        [--cloud=CLOUDS]
                        [--format=FORMAT]
                        [--refresh]
                vm boot [--name=NAME]
                        [--cloud=CLOUD]
                        [--username=USERNAME]
                        [--image=IMAGE]
                        [--flavor=FLAVOR]
                        [--public]
                        [--secgroup=SECGROUPs]
                        [--key=KEY]
                        [--dryrun]
                vm boot [--n=COUNT]
                        [--cloud=CLOUD]
                        [--username=USERNAME]
                        [--image=IMAGE]
                        [--flavor=FLAVOR]
                        [--public]
                        [--secgroup=SECGROUPS]
                        [--key=KEY]
                        [--dryrun]
                vm run [--name=NAMES] [--username=USERNAME] [--dryrun] COMMAND
                vm script [--name=NAMES] [--username=USERNAME] [--dryrun] SCRIPT
                vm ip assign [NAMES]
                          [--cloud=CLOUD]
                vm ip show [NAMES]
                           [--group=GROUP]
                           [--cloud=CLOUD]
                           [--format=FORMAT]
                           [--refresh]
                vm ip inventory [NAMES]
                vm ssh [NAMES] [--username=USER]
                         [--quiet]
                         [--ip=IP]
                         [--key=KEY]
                         [--command=COMMAND]
                         [--modify-knownhosts]
                vm rename [OLDNAMES] [NEWNAMES] [--force] [--dryrun]
                vm wait [--cloud=CLOUD] [--interval=SECONDS]
                vm info [--cloud=CLOUD]
                        [--format=FORMAT]
                vm username USERNAME [NAMES] [--cloud=CLOUD]
                vm resize [NAMES] [--size=SIZE]

            Arguments:
                COMMAND        positional arguments, the commands you want to
                               execute on the server(e.g. ls -a) separated by ';',
                               you will get a return of executing result instead of login to
                               the server, note that type in -- is suggested before
                               you input the commands
                NAME           server name. By default it is set to the name of last vm from database.
                NAMES          server name. By default it is set to the name of last vm from database.
                KEYPAIR_NAME   Name of the vm keypair to be used to create VM. Note this is
                               not a path to key.
                NEWNAMES       New names of the VM while renaming.
                OLDNAMES       Old names of the VM while renaming.

            Options:
              -H --modify-knownhosts  Do not modify ~/.ssh/known_hosts file
                                      when ssh'ing into a machine
                --username=USERNAME   the username to login into the vm. If not
                                      specified it will be guessed
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
                --keypair_name=KEYPAIR_NAME   Name of the vm keypair to
                                              be used to create VM.
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
                    Displays default parameters that are set for vm boot either
                    on the default cloud or the specified cloud.

                vm boot [options...]
                    Boots servers on a cloud, user may specify flavor, image
                    .etc, otherwise default values will be used, see how to set
                    default values of a cloud: cloud help

                vm start [options...]
                    Starts a suspended or stopped vm instance.

                vm stop [options...]
                    Stops a vm instance .

                vm delete [options...]

                    Delete servers of a cloud, user may delete a server by its
                    name or id, delete servers of a group or servers of a cloud,
                    give prefix and/or range to find servers by their names.
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

        def map_parameters(arguments, *args):
            for arg in args:
                flag = "--" + arg
                if flag in arguments:
                    arguments[arg] = arguments[flag]
                else:
                    arguments[arg] = None

        def get_clouds(arguments, variables):

            clouds = arguments["cloud"] or arguments["--cloud"] or variables["cloud"]
            if "active" == clouds:
                active = Active()
                clouds = active.clouds()
            else:
                clouds = Parameter.expand(clouds)

            if clouds is None:
                Console.error("you need to specify a cloud")
                return None

            return clouds

        def get_names(arguments, variables):
            names = arguments["NAME"] or arguments["NAMES"] or arguments["--name"] or variables["vm"]
            if names is None:
                Console.error("you need to specify a vm")
                return None
            else:
                return Parameter.expand(names)

        def name_loop(names, label, f):
            names = get_names(arguments, variables)
            for name in names:
                Console.msg("{label} {name}".format(label=label, name=name))
                # r = f(name)

        map_parameters(arguments,
                       'active',
                       'cloud',
                       'command',
                       'dryrun',
                       'flavor',
                       'force',
                       'format',
                       'group',
                       'image',
                       'interval',
                       'ip',
                       'key',
                       'modify-knownhosts',
                       'n',
                       'name',
                       'public',
                       'quiet',
                       'refresh',
                       'secgroup',
                       'size',
                       'username')

        pprint(arguments)

        variables = Variables()

        if arguments.refresh:

            names = []

            if arguments["--cloud"]:
                clouds = get_clouds(arguments, variables)
                for cloud in clouds:
                    Console.msg("find names in cloud {cloud}".format(cloud=cloud))
                    # names = find all names in these clouds
            else:
                names = get_names(arguments, variables)

            for name in names:
                # r = vm.refresh(name)
                Console.msg("{label} {name}".format(label="refresh", name=name))
            return

        elif arguments.ping:

            names = []
            pings = int(arguments.N or 3)

            if arguments["--cloud"]:
                clouds = get_clouds(arguments, variables)
                for cloud in clouds:
                    Console.msg("find names in cloud {cloud}".format(cloud=cloud))
                    # names = find all names in these clouds
            else:
                names = get_names(arguments, variables)

            for name in names:
                # r = vm.ping(name)
                # result = Shell.ping(host=ip, count=n)
                # print(result)
                Console.msg("{label} {name}".format(label="ping", name=name))
            return

        elif arguments.check:

            names = []

            if arguments["--cloud"]:
                clouds = get_clouds(arguments, variables)
                for cloud in clouds:
                    Console.msg("find names in cloud {cloud}".format(cloud=cloud))
                    # names = find all names in these clouds
            else:
                names = get_names(arguments, variables)

            for name in names:
                # r = vm.check(name)
                Console.msg("{label} {name}".format(label="check", name=name))
            return

        elif arguments.status:

            names = []

            if arguments["--cloud"]:
                clouds = get_clouds(arguments, variables)
                for cloud in clouds:
                    Console.msg("find names in cloud {cloud}".format(cloud=cloud))
                    # names = find all names in these clouds
            else:
                names = get_names(arguments, variables)

            for name in names:
                # r = vm.check(name)
                Console.msg("{label} {name}".format(label="status", name=name))
            return

        elif arguments.start:

            names = []

            if arguments["--cloud"]:
                clouds = get_clouds(arguments, variables)
                for cloud in clouds:
                    Console.msg("find names in cloud {cloud}".format(cloud=cloud))
                    # names = find all names in these clouds
            else:
                names = get_names(arguments, variables)

            for name in names:
                # r = vm.start(name, dryrun=arguments.dryrun)
                Console.msg("{label} {name}".format(label="start", name=name))
            return

        elif arguments.stop:

            names = []

            if arguments["--cloud"]:
                clouds = get_clouds(arguments, variables)
                for cloud in clouds:
                    Console.msg("find names in cloud {cloud}".format(cloud=cloud))
                    # names = find all names in these clouds
            else:
                names = get_names(arguments, variables)

            for name in names:
                # r = vm.stop(name, dryrun=arguments.dryrun)
                Console.msg("{label} {name}".format(label="stop", name=name))
            return

        elif arguments.terminate:

            names = []

            if arguments["--cloud"]:
                clouds = get_clouds(arguments, variables)
                for cloud in clouds:
                    Console.msg("find names in cloud {cloud}".format(cloud=cloud))
                    # names = find all names in these clouds
            else:
                names = get_names(arguments, variables)

            for name in names:
                # r = vm.terminate(name, dryrun=arguments.dryrun)
                Console.msg("{label} {name}".format(label="terminate", name=name))
            return

        elif arguments.delete:

            names = []

            if arguments["--cloud"]:
                clouds = get_clouds(arguments, variables)
                for cloud in clouds:
                    Console.msg("find names in cloud {cloud}".format(cloud=cloud))
                    # names = find all names in these clouds
            else:
                names = get_names(arguments, variables)

            for name in names:
                # r = vm.delete(name, dryrun=arguments.dryrun)
                Console.msg("{label} {name}".format(label="delete", name=name))
            return

        elif arguments.boot:

            print("boot the vm")

        elif arguments.list:
            # vm list[NAMES]
            #   [--cloud = CLOUDS]
            #   [--format = FORMAT]
            #   [--refresh]

            # if no clouds find the clouds of all specified vms by name
            # find all vms of the clouds,
            # print only thos vms specified by name, if no name is given print all for the cloud
            print("list the vms")

        elif arguments.rename:

            print("rename the vm")


            try:
                oldnames = Parameter.expand(arguments["OLDNAMES"])
                newnames = Parameter.expand(arguments["NEWNAMES"])
                force = arguments["--force"]

                if oldnames is None or newnames is None:
                    Console.error("Wrong VMs specified for rename", traceflag=False)
                elif len(oldnames) != len(newnames):
                    Console.error("The number of VMs to be renamed is wrong",
                                  traceflag=False)
                else:
                    for i in range(0, len(oldnames)):
                        oldname = oldnames[i]
                        newname = newnames[i]
                        if arguments["--dryrun"]:
                            Console.ok("Rename {} to {}".format(oldname, newname))
                        else:
                            print("rename")
                            #
                            #Vm.rename(cloud=cloud,
                            #          oldname=oldname,
                            #          newname=newname,
                            #          force=force
                            #          )
                    msg = "info. OK."
                    Console.ok(msg)
            except Exception as e:
                # Error.traceback(e)
                Console.error("Problem deleting instances", traceflag=False)


        elif arguments["ip"] and arguments["show"]:

            print("show the ips")
            """
            vm ip show [NAMES]
                   [--group=GROUP]
                   [--cloud=CLOUD]
                   [--format=FORMAT]
                   [--refresh]

            """

        elif arguments["ip"] and arguments["assign"]:
            """
            vm ip assign [NAMES] [--cloud=CLOUD]
            """
            print("assign the public ip")

        elif arguments["ip"] and arguments["inventory"]:

            """
            vm ip inventory [NAMES]

            """
            print("list ips that could be assigned")

        elif arguments.username:

            """
            vm username USERNAME [NAMES] [--cloud=CLOUD]
            """
            print("sets the username for the vm")

        elif arguments.default:

            print("sets defaults for the vm")

        elif arguments.run:
            """
            vm run [--name=NAMES] [--username=USERNAME] [--dryrun] COMMAND

            """
            pass
        elif arguments.script:

            """
            vm script [--name=NAMES] [--username=USERNAME] [--dryrun] SCRIPT
            """
            pass

        elif arguments.resize:
            """
            vm resize [NAMES] [--size=SIZE]
            """
            pass

        elif arguments.ssh:

            """
            vm ssh [NAMES] [--username=USER]
                 [--quiet]
                 [--ip=IP]
                 [--key=KEY]
                 [--command=COMMAND]
                 [--modify-knownhosts]
            """
            print("ssh  the vm")

        elif arguments.console:
            # vm console [NAME] [--force]

            names = get_names(arguments, variables)

            for name in names:
                # r = vm.console(name,force=argument.force)
                Console.msg("{label} {name}".format(label="console", name=name))
            return

        elif arguments.info:

            """
            vm info [--cloud=CLOUD] [--format=FORMAT]
            """
            print("info for the vm")

        elif arguments.wait:
            """
            vm wait [--cloud=CLOUD] [--interval=SECONDS]
            """
            print("waits for the vm till its ready and one can login")



