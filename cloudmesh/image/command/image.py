from __future__ import print_function

from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from pprint import pprint

class ImageCommand(PluginCommand):

    # see https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/ImageCommand.py

    # noinspection PyUnusedLocal
    @command
    def do_image(self, args, arguments):
        """
        ::

            Usage:
                image refresh [--cloud=CLOUD]
                image list [--names=NAMES] [--cloud=CLOUD] [--refresh] [--format=FORMAT]

            Options:
               --format=FORMAT  the output format [default: table]
               --cloud=CLOUD    the cloud name
               --refresh        live data taken from the cloud

            Description:
                cm image refresh
                cm image list
                cm image list --format=csv
                cm image list 58c9552c-8d93-42c0-9dea-5f48d90a3188 --refresh
        """

        pprint(arguments)

        # m = Manager()

        # if arguments.FILE:
        #    print("option a")
        #    m.list(arguments.FILE)

        # elif arguments.list:
        #    print("option b")
        #    m.list("just calling list without parameter")
