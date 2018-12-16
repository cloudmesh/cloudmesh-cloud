from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cm4.configuration.config import Config
from cm4.vm.Vm import Vm
from pprint import pprint

# from cloudmesh.vm.api.manager import Manager

class VmCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_vm(self, args, arguments):
        """
        ::

          Usage:

            vm create [VMNAME] [--count=VMNUMBER] [--debug] [--dryrun]
            vm start [VMNAME] [--vms=VMLIST] [--count=VMNUMBER] [--debug] [--dryrun]
            vm stop [--vms=VMLIST] [--debug] [--dryrun]
            vm destroy [--vms=VMLIST] [--debug] [--dryrun]
            vm status [--vms=VMLIST] [--dryrun]
            vm list
            vm resize [SIZE]
            vm rebuild [IMAGE]
            vm rename [NAME]
            vm publicip [--vms=VMLIST]
            vm ssh NAME
            vm run COMMAND  [--vms=<vmList>]
            vm script run SCRIPT [--vms=<vmList>] [--dryrun]

          This command does some useful things.

          Arguments:
              FILE   a file name

          Options:
              -f      specify the file

        """

        print(arguments)

        def vm_manager():
            config = Config()
            default_cloud = config.data["cloudmesh"]["default"]["cloud"]
            vm = Vm(default_cloud)
            return vm

        result = None

        if arguments.get("--debug"):
            pp = pprint.PrettyPrinter(indent=4)
            print("vm processing arguments")
            pp.pprint(arguments)
            # pp.pprint(config.data)

        if arguments.get("list"):
            vm = vm_manager()
            result = vm.nodes()

        elif arguments.get("start"):
            vm = vm_manager()

            try:
                result = vm.start(arguments.get("--vms"))
            except ValueError:
                vm_name = arguments.get("VMNAME")
                vm.create(vm_name)
                result = f"Created {vm_name}"

        elif arguments.get("stop"):
            vm = vm_manager()

            result = vm.stop(arguments.get("--vms"))

        elif arguments.get("destroy"):
            vm = vm_manager()

            result = vm.destroy(arguments.get("--vms"))

        elif arguments.get("status"):
            vm = vm_manager()

            result = vm.status(arguments.get("--vms"))

        elif arguments.get("publicip"):
            vm = vm_manager()

            result = vm.get_public_ips(arguments.get('--vms'))

        elif arguments.get("ssh"):

            vm = vm_manager()

            # TODO
            raise NotImplementedError("cm4 vm ssh command has not yet been implemented")

        elif arguments.get("run"):

            vm = vm_manager()

            # TODO
            raise NotImplementedError("cm4 vm run command has not yet been implemented")

        elif arguments.get("script"):

            vm = vm_manager()

            # TODO
            raise NotImplementedError("cm4 vm script command has not yet been implemented")

        return result
