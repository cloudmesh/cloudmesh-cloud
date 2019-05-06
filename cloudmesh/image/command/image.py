from __future__ import print_function

from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters
from pprint import pprint
from cloudmesh.DEBUG import VERBOSE
from cloudmesh.variables import Variables
from cloudmesh.management.configuration.arguments import Arguments
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.common.Printer import Printer


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
                cm image list
                cm image list --output=csv
                cm image list 58c9552c-8d93-42c0-9dea-5f48d90a3188 --refresh
        """

        map_parameters(arguments,
                       "refresh",
                       "cloud",
                       "output")

        VERBOSE(arguments)

        variables = Variables()

        if arguments.list and arguments["--query"]:
            names = []

            clouds, names = Arguments.get_cloud_and_names("list", arguments,
                                                          variables)
            cloud = clouds[0]
            query = arguments["--query"]

            provider = Provider(name=cloud)

            ### implementation failed.
            ### couldn't find ducumentation suggesting the content of ex_filter other than it's a dict
            # if cloud == 'aws':
            #     filter = {}
            #     images = provider.images(ex_filter=filter)
            images = []
            #
            # images = provider.images(query=query)
            #

            order = provider.p.output['image']['order']  # not pretty
            header = provider.p.output['image']['header']  # not pretty

            print(Printer.flatwrite(images,
                                    sort_keys=["name"],
                                    order=order,
                                    header=header,
                                    output=arguments.output)
                  )
            return ""


        if arguments.list and arguments.refresh:

            names = []

            clouds, names = Arguments.get_cloud_and_names("list", arguments,
                                                          variables)


            for cloud in clouds:
                print(f"cloud {cloud}")
                provider = Provider(name=cloud)
                images = provider.images()

                order = provider.p.output['image']['order']  # not pretty
                header = provider.p.output['image']['header']  # not pretty

                print(Printer.flatwrite(images,
                                        sort_keys=["name"],
                                        order=order,
                                        header=header,
                                        output=arguments.output)
                      )
            return ""



        elif arguments.list:

            names = []

            clouds, names = Arguments.get_cloud_and_names("list", arguments,
                                                          variables)

            print(clouds, names)
            try:

                for cloud in clouds:
                    print(f"List {cloud}")
                    p = Provider(cloud)
                    kind = p.kind

                    collection = "{cloud}-image".format(cloud=cloud,
                                                        kind=p.kind)
                    db = CmDatabase()
                    vms = db.find(collection=collection)

                    order = p.p.output['image']['order']  # not pretty
                    header = p.p.output['image']['header']  # not pretty

                    print(Printer.flatwrite(vms,
                                            sort_keys=["name"],
                                            order=order,
                                            header=header,
                                            output=arguments.output)
                          )

            except Exception as e:

                VERBOSE(e)

            return ""
