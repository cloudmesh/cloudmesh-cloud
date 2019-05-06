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

        map_parameters(arguments,
                       "refresh",
                       "cloud",
                       "output")

        VERBOSE(arguments)

        variables = Variables()

        if arguments.list and arguments.refresh:

            names = []

            clouds, names = Arguments.get_cloud_and_names("list", arguments,
                                                          variables)


            for cloud in clouds:
                print(f"cloud {cloud}")
                provider = Provider(name=cloud)
                flavors = provider.flavors()

                order = provider.p.output['flavor']['order']  # not pretty
                header = provider.p.output['flavor']['header']  # not pretty

                print(Printer.flatwrite(flavors,
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

                    collection = "{cloud}-flavor".format(cloud=cloud,
                                                        kind=p.kind)
                    db = CmDatabase()
                    vms = db.find(collection=collection)

                    order = p.p.output['vm']['order']  # not pretty
                    header = p.p.output['vm']['header']  # not pretty

                    print(Printer.flatwrite(vms,
                                            sort_keys=["name"],
                                            order=order,
                                            header=header,
                                            output=arguments.output)
                          )

            except Exception as e:

                VERBOSE(e)

            return ""

        # if arguments.FILE:
        #    print("option a")
        #    m.list(arguments.FILE)

        # elif arguments.list:
        #    print("option b")
        #    m.list("just calling list without parameter")
