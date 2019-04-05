from __future__ import print_function

from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command


class FlavorCommand(PluginCommand):

    # see https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/FlavorCommand.py

    # noinspection PyUnusedLocal
    @command
    def do_flavor(self, args, arguments):
        """
        ::

            Usage:
                flavor list [NAMES] [--cloud=CLOUD] [--refresh] [--output=OUTPUT]


            Options:
               --output=OUTPUT  the output format [default: table]
               --cloud=CLOUD    the cloud name
               --refresh        refreshes the data before displaying it

            Description:

                This lists out the flavors present for a cloud

            Examples:
                cm flavor refresh
                cm flavor list
                cm flavor list --output=csv
                cm flavor list 58c9552c-8d93-42c0-9dea-5f48d90a3188 --refresh

                please remember that a uuid or the falvor name can be used to
                identify a flavor.
        """

        print(arguments)



        # if arguments.FILE:
        #    print("option a")
        #    m.list(arguments.FILE)

        # elif arguments.list:
        #    print("option b")
        #    m.list("just calling list without parameter")
