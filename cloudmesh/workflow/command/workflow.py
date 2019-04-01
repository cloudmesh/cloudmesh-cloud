from __future__ import print_function

from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command


class WorkflowCommand(PluginCommand):

    # see https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/WorkflowCommand.py

    # noinspection PyUnusedLocal
    @command
    def do_workflow(self, args, arguments):
        """
        ::

            Usage:
                workflow refresh [--cloud=CLOUD] [-v]
                workflow list [ID] [NAME] [--cloud=CLOUD] [--output=OUTPUT] [--refresh] [-v]
                workflow add NAME LOCATION
                workflow delete ID
                workflow status [NAMES]
                workflow show ID
                workflow save NAME WORKFLOWSTR
                workflow run NAME
                workflow service start
                workflow service stop
                This lists out the workflows present for a cloud

            Options:
               --output=OUTPUT  the output format [default: table]
               --cloud=CLOUD    the cloud name
               --refresh        refreshes the data before displaying it
                                from the cloud

            Examples:
                cm workflow refresh
                cm workflow list
                cm workflow list --format=csv
                cm workflow show 58c9552c-8d93-42c0-9dea-5f48d90a3188 --refresh
                cm workflow run workflow1
        """

        print(arguments)

        # m = Manager()

        # if arguments.FILE:
        #    print("option a")
        #    m.list(arguments.FILE)

        # elif arguments.list:
        #    print("option b")
        #    m.list("just calling list without parameter")
