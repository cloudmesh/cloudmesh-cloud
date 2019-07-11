import os.path
import webbrowser
from pathlib import Path

from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.mongo.MongoDBController import MongoDBController


class StopCommand(PluginCommand):

    # noinspection PyUnusedLocal,PyBroadException
    @command
    def do_stop(self, args, arguments):
        """
        ::

            Usage:
                stop

            Description:

                stops cloudmesh

        """

        print("MongoDB stop")
        MongoDBController().stop()
