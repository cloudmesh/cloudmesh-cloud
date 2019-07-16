from cloudmesh.common.debug import VERBOSE
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.management.configuration.arguments import Arguments
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters
from cloudmesh.common.variables import Variables


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
                cm flavor list --refresh
                cm flavor list
                cm flavor list --output=csv
                cm flavor list 58c9552c-8d93-42c0-9dea-5f48d90a3188 --refresh

                please remember that a uuid or the falvor name can be used to
                identify a flavor.
        """

        map_parameters(arguments,
                       "refresh",
                       "cloud",
                       "output")

        variables = Variables()

        if arguments.list and arguments.refresh:

            names = []

            clouds, names = Arguments.get_cloud_and_names("list",
                                                          arguments,
                                                          variables)

            for cloud in clouds:
                print(f"cloud {cloud}")
                provider = Provider(name=cloud)
                flavors = provider.flavors()

                provider.Print(arguments.output, "flavor", flavors)

            return ""

        elif arguments.list:

            names = []

            clouds, names = Arguments.get_cloud_and_names("list",
                                                          arguments,
                                                          variables)

            print(clouds, names)
            try:

                for cloud in clouds:
                    print(f"List {cloud}")
                    p = Provider(cloud)

                    db = CmDatabase()
                    flavors = db.find(collection=f"{cloud}-flavor")

                    p.Print(arguments.output, "flavor", flavors)


            except Exception as e:

                VERBOSE(e)

            return ""
