from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from pprint import pprint
from cloudmesh.common.console import Console

class SetCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_set(self, args, arguments):
        """
        ::

          Usage:
            set VARIABLE=VALUE
            set VARIABLE VALUE

          Sets an interanl variable to the value

          Arguments:
            VARIABLE   the variable name
            VALUE      the VALUE

          Options:
            -f      specify the file

          Description:

            TBD

        """

        if "VARIABLE=VALUE" is not None:
            arguments.VARIABLE, arguments.VALUE = str(arguments["VARIABLE=VALUE"]).split("=")



        variable = arguments.VARIABLE
        value = arguments.VALUE

        # TODO: implement
        Console.error("Adding to config file or db not yet implemented.", traceflag=False)

        pprint(arguments)


        return ""
