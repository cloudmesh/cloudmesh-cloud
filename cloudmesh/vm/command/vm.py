from __future__ import print_function

from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.variables import Variables
from cloudmesh.common.console import Console
from pprint import pprint, pformat
from cloudmesh.common.parameter import Parameter
from cloudmesh.management.configuration.config import Active
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import banner
from cloudmesh.terminal.Terminal import VERBOSE
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
                FORMAT         the format
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
                --format=FORMAT   the format [default: table]
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

            Limitations:

                Azure: rename is not supported
        """

        def map_parameters(arguments, *args):
            for arg in args:
                flag = "--" + arg
                if flag in arguments:
                    arguments[arg] = arguments[flag]
                else:
                    arguments[arg] = None

        def get_cloud_and_names(label, arguments):
            names = []
            clouds = []
            if arguments["--cloud"]:
                clouds = get_clouds(arguments, variables)
            else:
                clouds = get_clouds(arguments, variables)

            names = get_names(arguments, variables)

            return clouds, names

        def get_clouds(arguments, variables):

            clouds = arguments["cloud"] or arguments["--cloud"] or variables[
                "cloud"]
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
            names = arguments["NAME"] or arguments["NAMES"] or arguments[
                "--name"] or variables["vm"]
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
                       'secgroup',
                       'size',
                       'username')

        VERBOSE.print(arguments, verbose=9)

        variables = Variables()

        if arguments.refresh:

            names = []

            clouds, names = get_cloud_and_names("refresh", arguments)

            return ""

        elif arguments.ping:

            names = []
            pings = int(arguments.N or 3)

            names = []

            clouds, names = get_cloud_and_names("ping", arguments)

            return ""

        elif arguments.check:

            names = []

            clouds, names = get_cloud_and_names("check", arguments)

            return ""

        elif arguments.status:

            names = []

            clouds, names = get_cloud_and_names("status", arguments)

            return ""

        elif arguments.start:

            names = []

            clouds, names = get_cloud_and_names("start", arguments)

            return ""

        elif arguments.stop:

            names = []

            clouds, names = get_cloud_and_names("stop", arguments)

            return ""

        elif arguments.terminate:

            names = []

            clouds, names = get_cloud_and_names("terminate", arguments)

            return ""

        elif arguments.delete:

            clouds, names = get_cloud_and_names("delete", arguments)

            return ""

        elif arguments.boot:

            print("boot the vm")

        elif arguments.list:
            # vm list [NAMES]
            #   [--cloud = CLOUDS]
            #   [--format = FORMAT]
            #   [--refresh]

            # if no clouds find the clouds of all specified vms by name
            # find all vms of the clouds,
            # print only thos vms specified by name, if no name is given print all for the cloud
            # print("list the vms")

            clouds, names = get_cloud_and_names("list", arguments)

            # print("Clouds:", clouds)

            if arguments.NAMES is not None:
                names = Parameter.expand(arguments.NAMES)
                Console.error("NAMES, not yet implemented" + str(names))

                try:
                    if arguments["--refresh"]:
                        pass
                        # find all clouds in db
                        # itterate over the clouds
                        # for each name in name queue, find it and add it to the cloud vm list
                        # for each cloud print the vms
                    else:
                        pass
                        # find all clouds in db
                        # itterate over all clouds
                        # find the vm with the name
                        # add it to the cloud list
                        # for each cloud print the vms
                except Exception as e:

                    VERBOSE.print(e, verbose=9)

                return ""
            else:
                try:
                    if arguments["--refresh"]:
                        for cloud in clouds:
                            Console.ok("refresh " + cloud)

                            p = Provider(cloud)
                            r = p.list()

                    for cloud in clouds:
                        p = Provider(cloud)
                        # pprint(p.__dict__)
                        # pprint(p.p.__dict__) # not pretty

                        kind = p.kind
                        collection = "{cloud}-{kind}".format(cloud=cloud,
                                                             kind=p.kind)
                        db = CmDatabase()
                        vms = db.find(collection=collection)

                        # pprint(vms)
                        # print(arguments.format)
                        # print(p.p.output['vm'])

                        order = p.p.output['vm']['order']  # not pretty
                        header = p.p.output['vm']['header']  # not pretty

                        print(Printer.flatwrite(vms,
                                                sort_keys=("name"),
                                                order=order,
                                                header=header,
                                                output=arguments.format)
                              )


                except Exception as e:

                    VERBOSE.print(e, verbose=9)



            return ""

        elif arguments.info:

            """
            vm info [--cloud=CLOUD] [--format=FORMAT]
            """
            print("info for the vm")


            cloud, names = get_cloud_and_names("info", arguments)



        elif arguments.rename:

            print("rename the vm")
            
            try:
                oldnames = Parameter.expand(arguments["OLDNAMES"])
                newnames = Parameter.expand(arguments["NEWNAMES"])
                force = arguments["--force"]

                if oldnames is None or newnames is None:
                    Console.error("Wrong VMs specified for rename",
                                  traceflag=False)
                elif len(oldnames) != len(newnames):
                    Console.error("The number of VMs to be renamed is wrong",
                                  traceflag=False)
                else:
                    for i in range(0, len(oldnames)):
                        oldname = oldnames[i]
                        newname = newnames[i]
                        if arguments["--dryrun"]:
                            Console.ok(
                                "Rename {} to {}".format(oldname, newname))
                        else:
                            print("rename")
                            #
                            # Vm.rename(cloud=cloud,
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



        elif arguments.wait:
            """
            vm wait [--cloud=CLOUD] [--interval=SECONDS]
            """
            print("waits for the vm till its ready and one can login")
