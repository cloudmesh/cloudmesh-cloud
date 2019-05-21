from pprint import pprint

from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command


class RegisterCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_register(self, args, arguments):
        """
        ::

          Usage:
              cms register aws [FILENAME] [--keep]


          This command adds the registrarion information the th cloudmesh
          yaml file. The permissions of theFILENAME will also be changed.
          A y/n question will be asked if the files with the filename shoudl
          be deleted after integration

          Arguments:
              FILENME   a filename in which the cloud credentials are stored

          Options:
              --keep    keeps the file with the filename.

        """

        # m = Manager()

        if arguments.KEY is None:
            arguments.KEY = "~/.ssh/id_rsa.pub"

        pprint(arguments)

        key = path_expand(arguments.KEY)

        Console.msg("Login with", key)
        Console.error("not implemented")

        return ""
