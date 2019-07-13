import os.path
import webbrowser
from pathlib import Path

from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.mongo.MongoDBController import MongoDBController

class StartCommand(PluginCommand):

    # noinspection PyUnusedLocal,PyBroadException
    @command
    def do_start(self, args, arguments):
        """
        ::

            Usage:
                start

            Description:

                starts cloudmesh

        """

        print("MongoDB start")
        MongoDBController().start(security=True)
