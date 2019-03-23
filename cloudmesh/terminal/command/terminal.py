from __future__ import print_function

import os

from cloudmesh.common.Shell import Shell
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters
from cloudmesh.terminal.Terminal import VERBOSE


class TerminalCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_terminal(self, args, arguments):
        """
        ::

          Usage:
              terminal [--os=OS]
                       [--command=COMMAND]
                       [--shell=SHELL]
                       [--interactive=INTERACTIVE]
                       [--window=WINDOW]

          Starts a docker container in interactive mode in a new terminal
          and executes the command in it.

          Arguments:
              --command=COMMAND   the command
              --os=OS        the os      [default: cloudmesh/book:latest]
              --shell=SHELL              [default: /bin/bash]
              --window=WINDOW            [default: True]
              --interactive=INTERACTIVE  [default: True]

          Options:
              -f      specify the file


          Description:
              terminal --os="cloudmesh/book:1.7" --command=ls
        """

        # m = Manager()

        map_parameters(arguments,
                       'os',
                       'command',
                       'interactive',
                       'shell',
                       'window')
        arguments.cwd = os.getcwd()

        if arguments.command is None:
            arguments.command = ""
        else:
            arguments.command += ";"

        VERBOSE.print(arguments, label='arguments', verbose=1)

        if arguments.os is None:
            Shell.terminal(command=arguments.command)
        else:

            if arguments.interactive.lower() in ['true', 'on']:
                arguments.interactive = "-it"
            else:
                arguments.interactive = ""
                arguments.shell = ""

            VERBOSE.print(arguments, label='arguments', verbose=1)

            command = "cd {cwd}; docker run -v {cwd}:{cwd} -w {cwd} --rm {interactive} {os} {command}{shell}".format(
                **arguments)
            print(command)
            Shell.terminal(command=command)

        return ""
