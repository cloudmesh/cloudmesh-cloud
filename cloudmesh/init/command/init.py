import os.path
import webbrowser
from pathlib import Path

from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.mongo.MongoDBController import MongoDBController
import shutil
from cloudmesh.common.util import path_expand

class InitCommand(PluginCommand):

    # noinspection PyUnusedLocal,PyBroadException
    @command
    def do_init(self, args, arguments):
        """
        ::

            Usage:
                init

            Description:

                inits cloudmesh

        """

        try:
            print("MongoDB stop")
            MongoDBController().stop()
        except:
            Console.ok("MongDB is not running. ok")

        try:
            location = path_expand('~/.cloudmesh/mongodb')
            print("MongoDB delete")
            shutil.rmtree(location)
        except:
            Console.error(f"deleting {location}")

        print("MongoDB create")
        os.system("cms admin mongo create")
        os.system("cms admin mongo start")

