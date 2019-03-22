from __future__ import print_function
from cloudmesh.shell.command import command, map_parameters
from cloudmesh.shell.command import PluginCommand
from cloudmesh.login.api.manager import Manager
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from pprint import pprint
from cloudmesh.terminal.Terminal import VERBOSE
from cloudmesh.common.Shell import Shell


class TerminalCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_terminal(self, args, arguments):
        """
        ::

          Usage:
              terminal [--os=OS] [--command=COMMAND]

          Starts a dockker container in interactive mode in a new terminal
          and executes the command in it.

          Arguments:
              --command=COMMAND   the command
              --os=OS        the os

          Options:
              -f      specify the file


          Description:
              terminal --os="cloudmesh/book" --command=ls
        """

        # m = Manager()

        map_parameters(arguments, 'os', 'command')

        VERBOSE.print(arguments, label='arguments', verbose=1)

        if arguments.os is None:
            Shell.terminal(command=arguments.command)
        else:
            if arguments.command is not None:
                arguments.command = '-c' + arguments.command
            else:
                arguments.command = ""

            command = "docker run -v `pwd` -w `pwd` --rm -it {os}  /bin/bash {command}".format(
                **arguments)
            print(command)
            Shell.terminal(command=command)

        Console.error("not implemented")

        return ""
