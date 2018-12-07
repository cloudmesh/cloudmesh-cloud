from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
# from cloudmesh.admin.api.manager import Manager
from cm4.mongo.MongoDBController import MongoDBController
from cm4.mongo.MongoDBController import MongoInstaller

class AdminCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_admin(self, args, arguments):
        """
        ::

        Usage:

          cm4 admin mongo install [--brew] [--download=PATH]
          cm4 admin mongo start
          cm4 admin mongo stop
          cm4 admin mongo backup FILENAME
          cm4 admin mongo load FILENAME
          cm4 admin mongo help

        The admin command performs some adminsitrative functions, such as installing packages, software and services.
        It also is used to start services and configure them.

          Arguments:
              FILENAME   a filename
              PATH       the url to a file to be downloaded containing mongo
          Options:
              --brew     use brew on macOS to install mongo

        """
        arguments.PATH = arguments['--download'] or None

        # print(arguments)

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
