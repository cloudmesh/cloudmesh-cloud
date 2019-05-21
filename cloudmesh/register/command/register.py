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
              cms register azure [FILENAME] [--keep]
              cms register google [FILENAME] [--keep]
              cms register chameleon [FILENAME] [--keep]


          This command adds the registrarion information the th cloudmesh
          yaml file. The permissions of theFILENAME will also be changed.
          A y/n question will be asked if the files with the filename shoudl
          be deleted after integration

          Arguments:
              FILENME   a filename in which the cloud credentials are stored

          Options:
              --keep    keeps the file with the filename.

          Description:

            AWS

                AWS dependent on how you downloaded the creadentials will either
                use the filename `credentials.csv` or `accessKey.csv`

                Our command is smart provides some convenience functionality.


                1. If either file is found in ~/Downloads, it is moved to
                   ~/.cloudmesh and the permissions are changed
                2. If such a file already exists there it will ask if it should
                   be overwritten in case the content is not the same
                3. The content of the file will be read to determine if it is
                   likely to be an AWS credential
                4. The credential will be added to the cloudmesh yaml file

            Azure

                Is not yet implemented

            Google

                Is not yet implemented

            Chameleon Cloud

                is not yet implemented
        """

        if arguments.aws:

            Console.error("not yet implemented")

        elif arguments.azure:

            Console.error("not yet implemented")

        elif arguments.google:

            Console.error("not yet implemented")

        elif arguments.chameleon:

            Console.error("not yet implemented")

        return ""
