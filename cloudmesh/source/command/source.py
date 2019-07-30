from cloudmesh.common.Printer import Printer
from cloudmesh.configuration.Config import Config
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters
from cloudmesh.source.Source import Source


class SourceCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_source(self, args, arguments):
        """
        ::

          Usage:
              source list
              source install [--protocol=PROTOCOL]


          This command does some useful things.

          Arguments:
              KEY   a file name

          Options:
              -f      specify the file
              --protocol=PROTOCOL   [default: ssh]
              --output=OUTPUT       [default: table]

          Description:

             you cen specify in your yaml file the location of where you
             manage your source code.

             cloudmesh:
                source:
                  common: ~/Desktop/github/cloudmesh
                  cmd5: ~/Desktop/github/cloudmesh
                  openapi: ~/Desktop/github/cloudmesh
                  sys: ~/Desktop/github/cloudmesh
                  cm: ~/Desktop/github/cloudmesh-community


            Once you have this included and cms cm is installed, you can than for
            example do an update from source with

                cms source install

            This has the advantage that all cms directories pull the new code
            from git. It assumes that you have installed the source
            previously with

                pip install -e .

            in each of the directories

        """

        #

        map_parameters(arguments, "source", "protocol")

        config = Config()["cloudmesh.source"]
        m = Source(config, protocol=arguments.protocol)

        if arguments.list:

            print(Printer.attribute(config, output=arguments["output"]))

        elif arguments["install"]:

            m.install()

        elif arguments.clone:

            m.clone()

        elif arguments.update:

            m.update()

        return ""
