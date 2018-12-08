from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
# from cloudmesh.admin.api.manager import Manager
from cm4.mongo.MongoDBController import MongoDBController
from cm4.mongo.MongoDBController import MongoInstaller

"""
        ::

            Usage:

              cms admin mongo install [--brew] [--download=PATH]
             

              

"""

class AdminCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_admin(self, args, arguments):
        """
        ::

          Usage:
            admin mongo install [--brew] [--download=PATH]
            admin mongo start
            admin mongo stop
            admin mongo backup FILENAME
            admin mongo load FILENAME

          The admin command performs some adminsitrative functions, such as installing packages, software and services.
          It also is used to start services and configure them.

          Arguments:
            FILENAME  the filename for backups

          Options:
            -f      specify the file

          Description:

            TBD

        """

        # arguments.PATH = arguments['--download'] or None


        result = None

        if arguments.install:

            print("install")
            print("========")
            installer = MongoInstaller()
            r = installer.install()
            return r

        elif arguments.security:
            mongo = MongoDBController()
            mongo.set_auth()
            print()

        elif arguments.start:

            print("start")

        elif arguments.stop:

            print("stop")

        elif arguments.backup:

            print("backup")

        elif arguments.load:

            print("backup")

        elif arguments.status:

            mongo = MongoDBController()
            r = mongo.status()
            return r

        return result
