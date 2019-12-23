from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.variables import Variables
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.management.configuration.arguments import Arguments
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters


class FlavorCommand(PluginCommand):

    # see https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/FlavorCommand.py

    # noinspection PyUnusedLocal
    @command
    def do_flavor(self, args, arguments):
        """
        ::

            Usage:
                flavor list [NAMES] [--cloud=CLOUD] [--refresh] [--output=OUTPUT] [--query=QUERY]


            Options:
               --output=OUTPUT  the output format [default: table]
               --cloud=CLOUD    the ycloud name
               --refresh        refreshes the data before displaying it

            Description:

                This lists out the flavors present for a cloud

            Examples:
                cm flavor list --refresh
                cm flavor list
                cm flavor list --output=csv
                cm flavor list 58c9552c-8d93-42c0-9dea-5f48d90a3188 --refresh

                please remember that a uuid or the flavor name can be used to
                identify a flavor.


                cms flavor list --refresh --query=\'{\"a\": \"b\"}\'

            OpenStack Query Example:

                cms flavor list --refresh --query=\'{\"minDisk\": \"80\"}\'
                cms flavor list --refresh --query=\'{\"name\": \"m1.large\"}\'

                supported query parameters for OpenStack:

                        min_disk
                        min_ram
                        name


        """

        map_parameters(arguments,
                       "query",
                       "refresh",
                       "cloud",
                       "output")

        variables = Variables()

        arguments.output = Parameter.find("output",
                                          arguments,
                                          variables,
                                          "table")

        arguments.refresh = Parameter.find_bool("refresh",
                                                arguments,
                                                variables)

        if arguments.list and arguments.refresh:

            names = []

            clouds, names = Arguments.get_cloud_and_names("list",
                                                          arguments,
                                                          variables)

            for cloud in clouds:
                print(f"cloud {cloud} query={arguments.query}")
                provider = Provider(name=cloud)
                if arguments.query is not None:
                    query = eval(arguments.query)
                    flavors = provider.flavors(**query)
                else:

                    flavors = provider.flavors()

                provider.Print(flavors, output=arguments.output, kind="flavor")

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
                    provider = Provider(cloud)

                    db = CmDatabase()
                    flavors = db.find(collection=f"{cloud}-flavor")

                    provider.Print(flavors, output=arguments.output,
                                   kind="flavor")

            except Exception as e:

                VERBOSE(e)

            return ""
