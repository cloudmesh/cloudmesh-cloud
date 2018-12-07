from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
import hostlist
from termcolor import colored
import os
import logging

class VboxCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_vbox(self, args, arguments):
        """
        ::

            Vagrant Manager. This command will be deprected and replaced with vm

            Usage:
              cms vbox create --vms=VMLIST [--box=BOX] [--template=TEMPLATE] [--output=OUTPUT] [--debug]
              cms vbox start [--vms=VMLIST] [--debug]
              cms vbox resume [--vms=VMLIST] [--debug]
              cms vbox stop [--vms=VMLIST] [--debug]
              cms vbox suspend [--vms=VMLIST] [--debug]
              cms vbox destroy [-f] [--vms=VMLIST] [--debug]
              cms vbox info NAME [--debug]
              cms vbox ls [--debug]
              cms vbox upload --from=FROM --to=TO [-r] [--vms=VMLIST] [--debug]
              cms vbox download --from=FROM --to=TO [-r] [--vms=VMLIST] [--debug]
              cms vbox ssh NAME [--debug]
              cms vbox run command COMMAND [--vms=VMLIST] [--debug]
              cms vbox run script SCRIPT [--data=PATH] [--vms=VMLIST] [--debug]

              cm4 -h

            Options:
              -h --help     Show this screen.
              --vm_list=<list_of_vms>  List of VMs separated by commas ex: node-1,node-2

            Description:
               put a description here

            Example:
               put an example here
        """

        debug = arguments["--debug"]
        #    print(arguments)
        if debug:
            try:
                columns, rows = os.get_terminal_size(0)
            except OSError:
                columns, rows = os.get_terminal_size(1)

            print(colored(columns * '=', "red"))
            print(colored("Running in Debug Mode", "red"))
            print(colored(columns * '=', "red"))
            print(arguments)
            print(colored(columns * '-', "red"))
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        if arguments.get("vagrant"):

            provider = Vagrant(debug=debug)

            # parse argument
            action = None
            kwargs = dict()
            args = []
            if arguments.get("create"):
                action = provider.create
                kwargs = provider._update_by_key(kwargs, arguments, ['--image', '--template', '--count'],
                                                 {'--output': 'output_path'})
            elif arguments.get("start"):
                action = provider.start
            elif arguments.get("resume"):
                action = provider.start
            elif arguments.get("stop"):
                action = provider.stop
            elif arguments.get("suspend"):
                action = provider.suspend
            elif arguments.get("destroy"):
                action = provider.destroy
                kwargs = provider._update_by_key(kwargs, arguments, [], {'-f': 'force'})
            elif arguments.get("status"):
                action = provider.status
                args.append(arguments.get("NAME"))
            elif arguments.get("list"):
                action = provider.list
            elif arguments.get("download"):
                action = provider.download
                args.append(arguments.get("--from"))
                args.append(arguments.get("--to"))
                kwargs = provider._update_by_key(kwargs, arguments, key_dict={'-r': 'recursive'})
            elif arguments.get("upload"):
                action = provider.upload
                args.append(arguments.get("--from"))
                args.append(arguments.get("--to"))
                kwargs = provider._update_by_key(kwargs, arguments, key_dict={'-r': 'recursive'})
            elif arguments.get("ssh"):
                action = provider.ssh
                args.append(arguments.get("NAME"))
            elif arguments.get("run") and not arguments.get("script"):
                action = provider.run_command
                args.append(arguments.get("COMMAND"))
            elif arguments.get("script") and arguments.get("run"):
                action = provider.run_script
                args.append(arguments.get("SCRIPT"))
                kwargs = provider._update_by_key(kwargs, arguments, ['--data'])

            # do the action
            if action is not None:

                action_type = action.__name__

                # 1. aciton that can be immediately executed
                if action_type in ['ssh', 'list', 'create']:
                    action(*args, **kwargs)
                    return

                # parse vms_hosts
                if arguments.get("--vms"):
                    vms_hosts = arguments.get("--vms")
                    vms_hosts = hostlist.expand_hostlist(vms_hosts)
                else:
                    vms_hosts = []

                # 2. action can executed with original vms_hosts
                if action_type in ['start', 'resume', 'stop', 'suspend', 'destroy'] and not vms_hosts:
                    action(*args, **kwargs)
                    return
                elif action_type in ['status'] and not vms_hosts:
                    provider.list()
                    return

                # impute hosts
                if not vms_hosts:
                    hosts = provider._get_host_names()
                    if not hosts:
                        raise EnvironmentError('There is no host exists in the current vagrant project')
                else:
                    hosts = vms_hosts

                # 3. action work with imputed host
                if action_type in ['start', 'resume', 'stop', 'suspend', 'destroy', 'status']:
                    for node_name in hosts:
                        action(node_name, *args, **kwargs)
                else:
                    # impute argument according to number of host
                    if len(hosts) > 1:
                        if action_type in ['run_command', 'run_script']:
                            kwargs.update({'report_alone': False})
                        if action_type in ['download']:
                            kwargs.update({'prefix_dest': True})

                        provider.run_parallel(hosts, action, args, kwargs)

                    else:
                        if action_type in ['run_command', 'run_script']:
                            kwargs.update({'report_alone': True})
                        if action_type in ['download']:
                            kwargs.update({'prefix_dest': False})
                        action(hosts[0], *args, **kwargs)

