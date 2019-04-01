from __future__ import print_function

from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters
from pprint import pprint
from cloudmesh.terminal.Terminal import VERBOSE
from cloudmesh.shell.variables import Variables
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
                image list [NAMES] [--cloud=CLOUD] [--refresh] [--format=FORMAT]

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

        map_parameters(arguments,
                       "refresh",
                       "cloud",
                       "format")

        VERBOSE.print(arguments, verbose=9)

        variables = Variables()

        if arguments.list and arguments.refresh:

            names = []

            clouds, names = Arguments.get_cloud_and_names("list", arguments,
                                                          variables)

            print("AAA", clouds, names)

            for cloud in clouds:
                print(f"cloud {cloud}")
                provider = Provider(name=cloud)
                images = provider.images()

                # pprint(images)

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

                    # pprint(p.__dict__)
                    # pprint(p.p.__dict__) # not pretty

                    collection = "{cloud}-node".format(cloud=cloud,
                                                       kind=p.kind)
                    db = CmDatabase()
                    vms = db.find(collection=collection)

                    # pprint(vms)
                    # print(arguments.format)
                    # print(p.p.output['vm'])

                    order = p.p.output['vm']['order']  # not pretty
                    header = p.p.output['vm']['header']  # not pretty

                    print(Printer.flatwrite(vms,
                                            sort_keys=["name"],
                                            order=order,
                                            header=header,
                                            output=arguments.format)
                          )

            except Exception as e:

                VERBOSE.print(e, verbose=9)

            return ""
