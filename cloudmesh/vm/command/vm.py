import hashlib
from datetime import datetime
from pprint import pprint
import sys
import os

from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.error import Error
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.Host import Host
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.management.configuration.arguments import Arguments
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters
from cloudmesh.common.variables import Variables
from cloudmesh.common.Shell import Shell
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.dotdict import dotdict
from cloudmesh.configuration.Config import Config
from cloudmesh.management.configuration.name import Name
from cloudmesh.common.util import banner
from cloudmesh.image.Image import Image


class VmCommand(PluginCommand):

    # see also https://github.com/cloudmesh/client/edit/master/cloudmesh_client/shell/plugins/VmCommand.py

    # noinspection PyUnusedLocal
    @command
    def do_vm(self, args, arguments):
        """
        ::

            Usage:
                vm ping [NAMES] [--cloud=CLOUDS] [--count=N]
                vm check [NAMES] [--cloud=CLOUDS] [--username=USERNAME]
                vm status [NAMES] [--cloud=CLOUDS] [--output=OUTPUT]
                vm console [NAME] [--force]
                vm log [NAME] [--force]
                vm stop [NAMES]  [--dryrun]
                vm start [NAMES] [--dryrun]
                vm terminate [NAMES] [--cloud=CLOUD] [--dryrun]
                vm delete [NAMES] [--cloud=CLOUD] [--dryrun]
                vm refresh [--cloud=CLOUDS]
                vm list [NAMES]
                        [--cloud=CLOUDS]
                        [--output=OUTPUT]
                        [--refresh]
                vm boot [--n=COUNT]
                        [--name=VMNAMES]
                        [--cloud=CLOUD]
                        [--username=USERNAME]
                        [--image=IMAGE]
                        [--flavor=FLAVOR]
                        [--network=NETWORK]
                        [--public]
                        [--secgroup=SECGROUPs]
                        [--group=GROUPs]
                        [--key=KEY]
                        [--dryrun]
                        [-v]
                vm meta list [NAME]
                vm meta set [NAME] KEY=VALUE...
                vm meta delete [NAME] KEY...
                vm script [NAMES]
                          [--username=USERNAME]
                          [--key=KEY]
                          [--dryrun]
                          [--dir=DESTINATION]
                          SCRIPT
                vm ip assign [NAMES]
                          [--cloud=CLOUD]
                vm ip show [NAMES]
                           [--group=GROUP]
                           [--cloud=CLOUD]
                           [--output=OUTPUT]
                           [--refresh]
                vm ip inventory [NAMES]
                vm ssh [NAMES]
                       [--username=USER]
                       [--quiet]
                       [--ip=IP]
                       [--key=KEY]
                       [--command=COMMAND]
                vm put SOURCE DESTINATION [NAMES]
                vm get SOURCE DESTINATION [NAMES]
                vm rename [OLDNAMES] [NEWNAMES] [--force] [--dryrun]
                vm wait [--cloud=CLOUD] [--interval=INTERVAL] [--timeout=TIMEOUT]
                vm info [NAMES] [--cloud=CLOUD] [--output=OUTPUT] [--dryrun]
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
                -v             verbose, prints the dict at the end
                --output=OUTPUT   the output format
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

                 cms vm ssh --command=\"uname -a\"

                       executes the uname command on the last booted vm

                 vm script [--name=NAMES]
                           [--username=USERNAME]
                           [--key=KEY]
                           [--dryrun]
                           [--dir=DESTINATION]
                           [--shell=SHELL]
                           SCRIPT

                    The script command copies a shell script to the specified vms
                    into the DESTINATION directory and than execute it. With
                    SHELL you can set the shell for executing the command,
                    this coudl even be a python interpreter. Examples for
                    SHELL are /bin/sh, /usr/bin/env python

                 vm put SOURCE DESTINATION [NAMES]

                     puts the file defined by SOURCE into the DESINATION folder
                    on the specified machines. If the file exists it is
                     overwritten, so be careful.

                 vm get SOURCE DESTINATION [NAMES]

                     gets  the file defined by SOURCE into the DESINATION folder
                     on the specified machines. The SOURCE is on the remote
                     machine. If one machine is specified, the SOURCE is the same
                     name as on the remote machine. If multiple machines are
                     specified, the name of the machine will be a prefix to the
                     filename. If the filenames exists, they will be overwritten,
                     so be careful.

              Tip:
                 give the VM name, but in a hostlist style, which is very
                 convenient when you need a range of VMs e.g. sample[1-3]
                 => ['sample1', 'sample2', 'sample3']
                sample[1-3,18] => ['sample1', 'sample2', 'sample3', 'sample18']

              Quoting commands:
                 cm vm login gregor-004 --command=\"uname -a\"

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
                       'group'
                       'output',
                       'group',
                       'image',
                       'interval',
                       'timeout',
                       'ip',
                       'key',
                       'modify-knownhosts',
                       'n',
                       'name',
                       'public',
                       'quiet',
                       'secgroup',
                       'size',
                       'username',
                       'output',
                       'count',
                       'network',
                       'refresh')

        variables = Variables()
        database = CmDatabase()

        arguments.output = Parameter.find("output",
                                          arguments,
                                          variables,
                                          "table")

        arguments.refresh = Parameter.find_bool("refresh",
                                                arguments,
                                                variables)

        if (arguments.meta and arguments.list):

            name = arguments.NAME
            if arguments.NAME is None:
                name = variables['vm']
                if name is None:
                    Console.error("No vm specified")

            cloud = "chameleon"
            # cloud = Parameter.find(arguments, variables)
            print(f"vm metadata for {name} on {cloud}")

            provider = Provider(name=cloud)
            r = provider.get_server_metadata(name)
            print(r)

        elif arguments.meta and arguments.set:

            metadata = {}
            pairs = arguments['KEY=VALUE']
            for pair in pairs:
                key, value = pair.split("=", 1)
                metadata[key] = value

            name = arguments.NAME
            if arguments.NAME is None:
                name = variables['vm']
                if name is None:
                    Console.error("No vm specified")

            cloud = "chameleon"
            # cloud = Parameter.find(arguments, variables)
            print(f"cloud {cloud} {name}")

            provider = Provider(name=cloud)
            provider.set_server_metadata(name, **metadata)
            r = provider.get_server_metadata(name)

            pprint(r)

        elif arguments.meta and arguments.delete:

            metadata = {}
            keys = arguments['KEY']

            name = arguments.NAME
            if arguments.NAME is None:
                name = variables['vm']
                if name is None:
                    Console.error("No vm specified")

            cloud = "chameleon"
            # cloud = Parameter.find(arguments, variables)
            print(f"cloud {cloud} {name}")

            provider = Provider(name=cloud)

            for key in keys:
                provider.delete_server_metadata(name, key)

            r = provider.get_server_metadata(name)

            pprint(r)

        elif arguments.list and arguments.refresh:

            names = []

            clouds, names = Arguments.get_cloud_and_names("list",
                                                          arguments,
                                                          variables)

            for cloud in clouds:
                print(f"cloud {cloud}")
                provider = Provider(name=cloud)
                vms = provider.list()

                provider.Print(vms, output=arguments.output, kind="vm")

                return ""

        elif arguments.list:

            names = []

            clouds, names = Arguments.get_cloud_and_names("list",
                                                          arguments,
                                                          variables)

            try:

                for cloud in clouds:
                    print(f"List {cloud}")
                    p = Provider(cloud)
                    kind = p.kind

                    collection = "{cloud}-vm".format(cloud=cloud,
                                                     kind=p.kind)
                    db = CmDatabase()
                    vms = db.find(collection=collection)

                    p.Print(vms, output=arguments.output, kind="vm")

            except Exception as e:
                Console.error("Error in listing ", traceflag=True)
                VERBOSE(e)

            return ""

        elif arguments.ping:

            """
            vm ping [NAMES] [--cloud=CLOUDS] [--count=N]
            """
            if arguments.NAMES:
                variables['vm'] = arguments.NAMES
            if arguments['--cloud']:
                variables['cloud'] = arguments['--cloud']
            clouds, names = Arguments.get_cloud_and_names("status",
                                                          arguments,
                                                          variables)

            count = arguments.count
            if arguments.count:
                count = int(count)
            else:
                count = 1

            def get_ips():
                ips = []
                for cloud in clouds:
                    params = {}
                    # gets public ips from database
                    cursor = database.db[f'{cloud}-vm']
                    for name in names:
                        for node in cursor.find({'name': name}):
                            ips.append(node['ip_public'])
                    ips = list(set(ips))
                    pprint(ips)
                return ips

            ips = get_ips()
            if len(ips) == 0:
                Console.warning("no public ip found.")
                for cloud in clouds:
                    print(f"refresh for cloud {cloud}")
                    provider = Provider(name=cloud)
                    vms = provider.list()
                ips = get_ips()

            if len(ips) == 0:
                Console.error("No vms with public IPS found.")
                Console.error("  Make sure to use cms vm list --refresh")

            for ip in ips:
                result = Shell.ping(host=ip, count=count)
                banner(ip)
                print(result)
                print()

        elif arguments.check:

            raise NotImplementedError
            """
            vm check [NAMES] [--cloud=CLOUDS] [--username=USERNAME]
            """
            """
            
            THIS IS ALL WRONG AS PROVIDER DEPENDENT !!!
            
            if arguments.NAMES:
                variables['vm'] = arguments.NAMES
            if arguments['--cloud']:
                variables['cloud'] = arguments['--cloud']
            clouds, names = Arguments.get_cloud_and_names("status", arguments, variables)

            for cloud in clouds:
                provider = Provider(cloud)
                params = {}

                params['key'] = \
                    provider.p.spec["credentials"]['EC2_PRIVATE_KEY_FILE_PATH'] + \
                    provider.p.spec["credentials"]['EC2_PRIVATE_KEY_FILE_NAME']

                params['username'] = arguments['--username']  # or get from db

                processors = arguments['--processors']
                if processors:
                    params['processors'] = int(processors[0])

                # gets public ips from database
                public_ips = []
                cursor = database.db['{cloud}-vm']
                for name in names:
                    for node in cursor.find({'name': name}):
                        public_ips.append(node['public_ips'])
                public_ips = [y for x in public_ips for y in x]

                Host.check(hosts=public_ips, **params)
            """

        elif arguments.status:
            if arguments.NAMES:
                variables['vm'] = arguments.NAMES
            if arguments['--cloud']:
                variables['cloud'] = arguments['--cloud']
            clouds, names = Arguments.get_cloud_and_names("status", arguments,
                                                          variables)

            # gets status from database
            for cloud in clouds:
                provider = Provider(cloud)
                status = []
                cursor = database.db[f'{cloud}-vm']
                print(cloud)
                for name in names:
                    for node in cursor.find({'name': name}):
                        status.append(node)

                provider.Print(status, output=arguments.output, kind="status")
                return ""


        elif arguments.start:
            # TODO: not tested
            if arguments.NAMES:
                names = variables['vm'] = arguments.NAMES

            if arguments['--cloud']:
                variables['cloud'] = arguments['--cloud']
            clouds, names = Arguments.get_cloud_and_names("stop", arguments,
                                                          variables)

            cloud = clouds[0]
            print(cloud)
            print(names)

            for name in names:

                provider = Provider(cloud)

                if arguments['--dryrun']:
                    print(f"start node {name}")
                else:
                    vms = provider.start(name=name, cloud=cloud)

                    provider.Print(vms, output=arguments.output, kind="vm")

            return ""

        elif arguments.stop:
            # TODO: not tested

            if arguments.NAMES:
                variables['vm'] = arguments.NAMES
            if arguments['--cloud']:
                variables['cloud'] = arguments['--cloud']
            clouds, names = Arguments.get_cloud_and_names("stop", arguments,
                                                          variables)

            for cloud in clouds:
                params = {}
                provider = Provider(cloud)

                if arguments['--dryrun']:
                    Console.ok(f"Dryrun stop: "
                               f"        {cloud}\n"
                               f"        {names}"
                               f"        {provider}")
                else:
                    for name in names:
                        vms = provider.stop(name)

                    provider.Print(vms, output=arguments.output, kind="vm")


        elif arguments.terminate:
            # TODO: not tested

            if arguments.NAMES:
                variables['vm'] = arguments.NAMES
            if arguments['--cloud']:
                variables['cloud'] = arguments['--cloud']
            clouds, names = Arguments.get_cloud_and_names("stop", arguments,
                                                          variables)

            for cloud in clouds:
                params = {}
                provider = Provider(cloud)

                if arguments['--dryrun']:
                    Console.ok(f"Dryrun terminate: "
                               f"        {cloud}\n"
                               f"        {names}"
                               f"        {provider}")
                else:
                    for name in names:
                        vms = provider.destroy(name)

                    provider.Print(vms, output=arguments.output, kind="vm")


        elif arguments.delete:

            if arguments.NAMES:
                variables['vm'] = arguments.NAMES
            if arguments['--cloud']:
                variables['cloud'] = arguments['--cloud']
            clouds, names = Arguments.get_cloud_and_names("stop", arguments,
                                                          variables)

            if names is not None:
                pass
            elif clouds is not None:
                for cloud in clouds:
                    provider = Provider(cloud)
                    vms = provider.list()
                    for vm in vms:
                        r = provider.destroy(name=vm)
                return ""
            else:
                return ""

            for cloud in clouds:
                provider = Provider(cloud)
                vms = provider.list()
                for vm in vms:
                    name = vm["cm"]["name"]
                    if name in names:
                        r = provider.destroy(name=name)



        # TODO: username, secgroup
        elif arguments.boot:
            # not everything works

            """
                vm boot 
                        [--name=VMNAMES]
                        [--cloud=CLOUD]
                        [--username=USERNAME]
                        [--image=IMAGE]
                        [--flavor=FLAVOR]
                        [--network=NETWORK]
                        [--public]
                        [--secgroup=SECGROUP]
                        [--key=KEY]
                        [--group=GROUP]
                        [--dryrun]
            """
            # for name in names:
            #    node = p.create(name=name, size=flavor, image=image)

            # VERBOSE(arguments)
            parameters = dotdict()

            names = Parameter.expand(arguments.name)

            cloud = Parameter.find("cloud",
                                   arguments,
                                   variables.dict())
            defaults = Config()[f"cloudmesh.cloud.{cloud}.default"]
            groups = Parameter.find("group",
                                    arguments,
                                    variables.dict(),
                                    {"group": "default"})

            parameters = dotdict()

            # parameters.names = arguments.name

            parameters.group = groups
            for attribute in ["image",
                              "username",
                              "flavor",
                              "key",
                              "network",
                              "secgroup"]:
                parameters[attribute] = Parameter.find(attribute,
                                                       arguments,
                                                       variables.dict(),
                                                       defaults)

            if arguments.username is None:
                parameters.user = Image.guess_username(parameters.image)

            provider = Provider(name=cloud)

            parameters.secgroup = arguments.secgroup or "default"

            #
            # determine names
            #

            if names and arguments.n and len(names) > 1:
                Console.error(
                    f"When using --n={arguments.n}, you can only specify one name")
                return ""
            # cases
            #

            # only name --name = "a[1,2]"
            # name and count # --name="a" --n=3, names must be of length 1
            # only count --n=2 names are read form var
            # nothing, just use one vm

            # determin names
            _names = []
            if not names:

                if not arguments.n:
                    count = 1
                else:
                    count = int(arguments.n)

                for i in range(0, count):
                    if names is None:
                        n = Name()
                        n.incr()
                        name = str(n)
                    else:
                        n = names[i]
                        name = str(n)
                    _names.append(name)
                names = _names

            elif len(names) == 1 and arguments.n:

                name = names[0]
                for i in range(0, int(arguments.n)):
                    _names.append(f"{name}-{i}")
                names = _names

            # pprint(parameters)

            for name in names:

                parameters.name = name
                if arguments['--dryrun']:
                    banner("boot")

                    pprint(parameters)

                    Console.ok(f"Dryrun boot {name}: \n"
                               f"        cloud={cloud}\n"
                               f"        names={names}\n"
                               f"        provider={provider}")
                    print()
                    for attribute in parameters:
                        value = parameters[attribute]
                        Console.ok(f"        {attribute}={value}")

                else:

                    # parameters.progress = len(parameters.names) < 2

                    try:
                        vms = provider.create(**parameters)
                    except TimeoutError:
                        Console.error(
                            f"Timeout during vm creation. There may be a problem with the cloud {cloud}")

                    except Exception as e:
                        Console.error("create problem", traceflag=True)
                        print(e)
                        return ""

                    variables['vm'] = str(n)
                    if arguments["-v"]:
                        banner("Details")
                        pprint(vms)

            # provider.Print(arguments.output, "vm", vms)

        elif arguments.info:
            """
            vm info [NAMES] [--cloud=CLOUD] [--output=OUTPUT] [--dryrun]
            """
            cloud, names = Arguments.get_cloud_and_names("info", arguments,
                                                         variables)

            cloud_kind = cloud[0]

            for name in names:
                #Get Cloud Provider.
                provider = Provider(cloud_kind)
                if arguments['--dryrun']:
                    print(f"info node {name}")
                else:
                    vms = provider.info(name=name)
                    provider.Print(vms, output=arguments.output, kind="vm")

            return ""

        elif arguments.rename:
            raise NotImplementedError
            # Not tested
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
                Console.error("Problem renaming instances", traceflag=True)

        elif arguments["ip"] and arguments["show"]:
            raise NotImplementedError

            print("show the ips")
            """
            vm ip show [NAMES]
                   [--group=GROUP]
                   [--cloud=CLOUD]
                   [--output=OUTPUT]
                   [--refresh]

            """

        elif arguments["ip"] and arguments["assign"]:
            raise NotImplementedError
            """
            vm ip assign [NAMES] [--cloud=CLOUD]
            """
            print("assign the public ip")

        elif arguments["ip"] and arguments["inventory"]:
            raise NotImplementedError

            """
            vm ip inventory [NAMES]

            """
            print("list ips that could be assigned")

        elif arguments.default:
            raise NotImplementedError

            print("sets defaults for the vm")

        elif arguments.script:
            raise NotImplementedError
            clouds, names = Arguments.get_cloud_and_names("run", arguments,
                                                          variables)
            username = arguments['--username']
            script = arguments.SCRIPT

            for cloud in clouds:
                provider = Provider(cloud)

                name_ips = {}
                cursor = database.db['{}-node'.format(cloud)]
                for name in names:
                    for node in cursor.find({'name': name}):
                        name_ips[name] = node['public_ips']

                if arguments['--dryrun']:
                    print("run script {} on vms: {}".format(script, names))
                else:
                    provider.ssh(name_ips, username=username, script=script)

        elif arguments.username:
            raise NotImplementedError

            """
            vm username USERNAME [NAMES] [--cloud=CLOUD]
            """
            print("sets the username for the vm")

        elif arguments.resize:
            raise NotImplementedError
            """
            vm resize [NAMES] [--size=SIZE]
            """
            pass

        elif arguments.ssh:

            """
            vm ssh [NAMES] 
                 [--username=USER]
                 [--quiet]
                 [--ip=IP]
                 [--key=KEY]
                 [--command=COMMAND]
            """

            # VERBOSE(arguments)
            clouds, names, command = Arguments.get_commands("ssh",
                                                            arguments,
                                                            variables)

            # print (clouds)
            # print(names)
            # print (command)

            if arguments.command is None and len(names) > 1:
                Console.error("Interactive shell can only be done on one vm")
                return ""
            elif arguments.command is None and len(names) == 1:
                name = names[0]
                cloud = clouds[0]
                cm = CmDatabase()
                try:
                    vm = cm.find_name(name, "vm")[0]
                except IndexError:
                    Console.error(f"could not find vm {name}")
                    return ""
                # VERBOSE(vm)
                cloud = vm["cm"]["cloud"]
                provider = Provider(name=cloud)
                try:
                    provider.ssh(vm=vm)
                except KeyError:
                    vms = provider.list()

                    provider.Print(vms, output=arguments.output, kind="vm")

                    provider.ssh(vm=vm)
                return ""
            else:
                # command on all vms

                if clouds is None or names is None or command is None:
                    return ""
                else:
                    for cloud in clouds:
                        p = Provider(cloud)
                        for name in names:
                            cm = CmDatabase()
                            try:
                                vm = cm.find_name(name, "vm")[0]
                            except IndexError:
                                Console.error(f"could not find vm {name}")
                                continue
                            r = p.ssh(vm=vm, command=command)
                            print(r)
            return ""

        elif arguments.console:

            # why is this not vm
            clouds, names, command = Arguments.get_commands("ssh",
                                                            arguments,
                                                            variables)

            print(clouds)
            print(names)
            print(command)

            for cloud in clouds:
                p = Provider(cloud)
                for name in names:
                    cm = CmDatabase()
                    try:
                        vm = cm.find_name(name, "vm")[0]
                    except IndexError:
                        Console.error(f"could not find vm {name}")
                        continue
                    r = p.console(vm=vm)
                    print(r)

            return ""

        elif arguments.log:

            # why is this not vm
            clouds, names, command = Arguments.get_commands("ssh",
                                                            arguments,
                                                            variables)

            print(clouds)
            print(names)
            print(command)

            for cloud in clouds:
                p = Provider(cloud)
                for name in names:
                    cm = CmDatabase()
                    try:
                        vm = cm.find_name(name, "vm")[0]
                    except IndexError:
                        Console.error(f"could not find vm {name}")
                        continue
                    r = p.log(vm=vm)
                    print(r)

            return ""

        elif arguments.wait:
            """
            vm wait [--cloud=CLOUD] [--interval=INTERVAL] [--timeout=TIMEOUT]
            """

            # why is this not vm
            clouds, names, command = Arguments.get_commands("ssh",
                                                            arguments,
                                                            variables)

            # print (clouds)
            # print (names)
            # print (command)

            for cloud in clouds:
                p = Provider(cloud)
                for name in names:
                    cm = CmDatabase()
                    try:
                        vm = cm.find_name(name, "vm")[0]
                    except IndexError:
                        Console.error(f"could not find vm {name}")
                        continue
                    r = p.wait(vm=vm, interval=arguments.interval,
                               timeout=arguments.timeout)
                    if r:
                        Console.ok("Instance available for SSH")
                    else:
                        Console.error(
                            f"Instance unavailable after timeout of {arguments.timeout}")
                    # print(r)

            return ""

        elif arguments.put:
            """
            vm put SOURCE DESTINATION
            """
            clouds, names, command = Arguments.get_commands("ssh",
                                                            arguments,
                                                            variables)

            key = variables['key']

            source = arguments['SOURCE']
            destination = arguments['DESTINATION']
            for cloud in clouds:
                p = Provider(name=cloud)
                cm = CmDatabase()
                for name in names:
                    try:
                        vms = cm.find_name(name, "vm")
                    except IndexError:
                        Console.error(f"could not find vm {name}")
                        return ""
                    # VERBOSE(vm)
                    for vm in vms:
                        try:
                            ip = vm['public_ips']
                        except:
                            try:
                                ip = p.get_public_ip(name=name)
                            except:
                                Console.error(
                                    f"could not find a public ip for vm {name}",
                                    traceflag=True)
                                return
                            Console.error(
                                f"could not find a public ip for vm {name}",
                                traceflag=True)
                            return

                        # get the username
                        try:
                            # username not in vm...guessing
                            imagename = list(
                                cm.collection(cloud + '-image').find(
                                    {'ImageId': vm['ImageId']}))[0][
                                'name']
                            print(imagename)
                            user = Image.guess_username(image=imagename,
                                                        cloud=cloud)
                        except:
                            try:
                                user = vm['os_profile']['admin_username']
                            except:
                                Console.error(
                                    f"could not find a valid username for "
                                    f"{name}, try refreshing the image list",
                                    traceflag=True)
                                return
                            Console.error(
                                f"could not find a valid username for {name}, try refreshing the image list")
                            return

                        cmd = f'scp -i {key} {source} {user}@{ip}:{destination}'
                        print(cmd)
                        os.system(cmd)
            return ""
