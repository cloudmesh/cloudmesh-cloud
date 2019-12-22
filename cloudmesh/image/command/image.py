from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.variables import Variables
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.management.configuration.arguments import Arguments
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters
from cloudmesh.common.parameter import Parameter


class ImageCommand(PluginCommand):

    # see https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/ImageCommand.py

    # noinspection PyUnusedLocal
    @command
    def do_image(self, args, arguments):
        """
        ::

            Usage:
                image list [NAMES] [--cloud=CLOUD] [--refresh] [--output=OUTPUT] [--query=QUERY]

            Options:
               --output=OUTPUT  the output format [default: table]
               --cloud=CLOUD    the cloud name
               --refresh        live data taken from the cloud

            Description:
                image list
                image list --cloud=aws --refresh
                image list --output=csv
                image list 58c9552c-8d93-42c0-9dea-5f48d90a3188 --refresh
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
        if arguments.list and arguments["--query"]:

            names = []

            clouds, names = Arguments.get_cloud_and_names("list",
                                                          arguments,
                                                          variables)

            for cloud in clouds:
                print(f"cloud {cloud} query={arguments.query}")
                provider = Provider(name=cloud)
                if arguments.query is not None:
                    query = eval(arguments.query)
                    images = provider.images(**query)
                else:
                    images = provider.images()

                provider.Print(images, output=arguments.output, kind="image")

            return ""

        if arguments.list and arguments.refresh:

            names = []

            clouds, names = Arguments.get_cloud_and_names("list",
                                                          arguments,
                                                          variables)

            for cloud in clouds:
                print(f"cloud {cloud}")
                provider = Provider(name=cloud)
                images = provider.images()

                provider.Print(images, output=arguments.output, kind="image")

            return ""

        elif arguments.list:

            clouds, names = Arguments.get_cloud_and_names("list",
                                                          arguments,
                                                          variables)

            print(clouds)
            print("find images")

            try:

                for cloud in clouds:
                    print(f"List {cloud} images")
                    provider = Provider(name=cloud)

                    db = CmDatabase()

                    images = db.find(collection=f"{cloud}-image")

                    provider.Print(images,
                                   output=arguments.output,
                                   kind="image")

            except Exception as e:

                VERBOSE(e)

            return ""
