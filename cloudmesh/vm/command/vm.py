from __future__ import print_function

from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.parameter import Parameter
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.management.configuration.config import Active
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters
from cloudmesh.shell.variables import Variables
from cloudmesh.terminal.Terminal import VERBOSE
from cloudmesh.management.configuration.arguments import Arguments
from cloudmesh.common.Shell import Shell
from cloudmesh.common.error import Error
from pprint import pprint

class VmCommand(PluginCommand):

    # see also https://github.com/cloudmesh/client/edit/master/cloudmesh_client/shell/plugins/VmCommand.py

    # noinspection PyUnusedLocal
    @command
    def do_vm(self, args, arguments):
        """
        ::

            Usage:
                vm ping [NAMES] [--cloud=CLOUDS] [--count=N] [--processors=PROCESSORS]
                vm check [NAMES] [--cloud=CLOUDS] [--processors=PROCESSORS]
                vm status [NAMES] [--cloud=CLOUDS]
                vm console [NAME] [--force]
                vm start [NAMES] [--cloud=CLOUD] [--dryrun]
                vm stop [NAMES] [--cloud=CLOUD] [--dryrun]
                vm terminate [NAMES] [--cloud=CLOUD] [--dryrun]
                vm delete [NAMES] [--cloud=CLOUD] [--dryrun]
                vm refresh [--cloud=CLOUDS]
                vm list [NAMES]
                        [--cloud=CLOUDS]
                        [--output=OUTPUT]
                        [--refresh]
                vm boot [--name=VMNAMES]
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
                vm run [--name=VMNAMES] [--username=USERNAME] [--dryrun] COMMAND
                vm script [--name=NAMES] [--username=USERNAME] [--dryrun] SCRIPT
                vm ip assign [NAMES]
                          [--cloud=CLOUD]
                vm ip show [NAMES]
                           [--group=GROUP]
                           [--cloud=CLOUD]
                           [--output=OUTPUT]
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
                        [--output=OUTPUT]
                vm username USERNAME [NAMES] [--cloud=CLOUD]
                vm resize [NAMES] [--size=SIZE]

            Arguments:
                OUTPUT         the output format
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
                --output=OUTPUT   the output format [default: table]
                -H --modify-knownhosts  Do not modify ~/.ssh/known_hosts file
                                      when ssh'ing into a machine
                --username=USERNAME   the username to login into the vm. If not
                                      specified it will be guessed
                                      from the image name and the cloud
                --ip=IP          give the public ip of the server
                --cloud=CLOUD    give a cloud to work on, if not given, selected
                                 or default cloud will be used
                --count=COUNT    give the number of servers to start
                --detail         for table, a brief version
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

                vm refresh [--cloud=CLOUDS]
                    this command refreshes the data for virtual machines,
                    images and flavors for the specified clouds.

                vm ping [NAMES] [--cloud=CLOUDS] [--count=N] [--processors=PROCESSORS]
                     pings the specified virtual machines, while using at most N pings.
                     The ping is executed in parallel.
                     If names are specifies the ping is restricted to the given names in
                     parameter format. If clouds are specified, names that are not in
                     these clouds are ignored. If the name is set in the variables
                     this name is used.

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

        map_parameters(arguments,
                       'active',
                       'cloud',
                       'command',
                       'dryrun',
                       'flavor',
                       'force',
                       'output',
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

            clouds, names = Arguments.get_cloud_and_names("refresh", arguments, variables)

            return ""

        elif arguments.ping:

            # TODO: IMPLEMENT
            names = []
            pings = int(arguments.N or 3)

            names = []

            clouds, names = Arguments.get_cloud_and_names("ping", arguments, variables)

            for name in names:

                ping = Shell.live(
                    "ping -c {N} {name}".format(name=name, N=arguments.N))
                print(ping)
            else:
                return True

            return ""

        elif arguments.check:

            names = []

            clouds, names = Arguments.get_cloud_and_names("check", arguments, variables)

            return ""

        elif arguments.status:

            names = []

            clouds, names = Arguments.get_cloud_and_names("status", arguments, variables)

            return ""

        elif arguments.start:

            names = []

            clouds, names = Arguments.get_cloud_and_names("start", arguments, variables)

            return ""

        elif arguments.stop:

            names = []

            clouds, names = Arguments.get_cloud_and_names("stop", arguments, variables)

            return ""

        elif arguments.terminate:

            names = []

            clouds, names = Arguments.get_cloud_and_names("terminate", arguments, variables)

            return ""

        elif arguments.delete:

            clouds, names = Arguments.get_cloud_and_names("delete", arguments, variables)

            return ""

        elif arguments.boot:

            print("boot the vm")

        elif arguments.list:
            # vm list [NAMES]
            #   [--cloud=CLOUDS]
            #   [--output=OUPTUT]
            #   [--refresh]

            # if no clouds find the clouds of all specified vms by name
            # find all vms of the clouds,
            # print only those vms specified by name, if no name is given print all for the cloud
            # print("list the vms")

            clouds, names = Arguments.get_cloud_and_names("list", arguments, variables)

            # print("Clouds:", clouds)

            if arguments.NAMES is not None:
                names = Parameter.expand(arguments.NAMES)
                Console.error("NAMES, not yet implemented" + str(names))

                try:
                    if arguments["--refresh"]:
                        pass
                        # find all clouds in db
                        # iterate over the clouds
                        # for each name in name queue, find it and add it to the cloud vm list
                        # for each cloud print the vms
                    else:
                        pass
                        # find all clouds in db
                        # iterate over all clouds
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
                            vms = p.list()

                            order = p.p.output['vm']['order']  # not pretty
                            header = p.p.output['vm']['header']  # not pretty

                            print(Printer.flatwrite(vms,
                                                    sort_keys=["cm.name"],
                                                    order=order,
                                                    header=header,
                                                    output=arguments.output)
                                  )

                    else:
                        for cloud in clouds:
                            p = Provider(cloud)
                            kind = p.kind

                            # pprint(p.__dict__)
                            # pprint(p.p.__dict__) # not pretty

                            collection = "{cloud}-node".format(cloud=cloud,
                                                               kind=p.kind)
                            db = CmDatabase()
                            vms = db.find(collection=collection)

                            # pprint(vms)
                            # print(arguments.output)
                            # print(p.p.output['vm'])

                            order = p.p.output['vm']['order']  # not pretty
                            header = p.p.output['vm']['header']  # not pretty


                            print(Printer.flatwrite(vms,
                                                    sort_keys=["cm.name"],
                                                    order=order,
                                                    header=header,
                                                    output=arguments.output)
                                  )

                except Exception as e:

                    VERBOSE.print(e, verbose=9)

            return ""

        elif arguments.info:

            """
            vm info [--cloud=CLOUD] [--output=OUTPUT]
            """
            print("info for the vm")

            cloud, names = Arguments.get_cloud_and_names("info", arguments, variables)

        elif arguments.rename:

            print("rename the vm")

            v = Variables()
            cloud = v["cloud"]

            p = Provider(cloud)

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
                    print(oldnames)
                    print(newnames)
                    for i in range(0, len(oldnames)):
                        oldname = oldnames[i]
                        newname = newnames[i]
                        if arguments["--dryrun"]:
                            Console.ok(
                                "Rename {} to {}".format(oldname, newname))
                        else:
                            print(f"rename {oldname} -> {newname}")


                            p.rename(source=oldname, destination=newname)

                    msg = "info. OK."
                    Console.ok(msg)
            except Exception as e:
                Error.traceback(e)
                Console.error("Problem renameing instances", traceflag=True)

        elif arguments["ip"] and arguments["show"]:

            print("show the ips")
            """
            vm ip show [NAMES]
                   [--group=GROUP]
                   [--cloud=CLOUD]
                   [--output=OUTPUT]
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

            names = Arguments.get_names(arguments, variables)

            for name in names:
                # r = vm.console(name,force=argument.force)
                Console.msg("{label} {name}".format(label="console", name=name))
            return

        elif arguments.wait:
            """
            vm wait [--cloud=CLOUD] [--interval=SECONDS]
            """
            print("waits for the vm till its ready and one can login")
