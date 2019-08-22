from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command


# see https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/WorkflowCommand.py

class Workflow_draftCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_workflow_draft(self, args, arguments):
        """
        ::

            Usage:
                workflow_draft refresh [--cloud=CLOUD] [-v]
                workflow_draft list [ID] [NAME] [--cloud=CLOUD] [--output=OUTPUT] [--refresh] [-v]
                workflow_draft add NAME LOCATION
                workflow_draft delete ID
                workflow_draft status [NAMES]
                workflow_draft show ID
                workflow_draft save NAME WORKFLOWSTR
                workflow_draft run NAME
                workflow_draft service start
                workflow_draft service stop

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
