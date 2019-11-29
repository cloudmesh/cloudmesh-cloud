from cloudmesh.mongo.MongoDBController import MongoDBController
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.common.console import Console


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
        if not MongoDBController().service_is_running():
            MongoDBController().start(security=True)
        else:
            Console.ok("MongoDB service is already running")
