from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand


# from cloudmesh.vm.api.manager import Manager

class VmCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_vm(self, args, arguments):
        """
        ::

          Usage:
                vm --file=FILE
                vm list

          This command does some useful things.

          Arguments:
              FILE   a file name

          Options:
              -f      specify the file

        """
        arguments.FILE = arguments['--file'] or None

        print(arguments)

        # m = Manager()

        if arguments.FILE:
            print("option a")
        #    m.list(arguments.FILE)

        elif arguments.list:
            print("option b")
        #    m.list("just calling list without parameter")
