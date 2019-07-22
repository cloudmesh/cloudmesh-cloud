from cloudmesh.mongo.MongoDBController import MongoDBController
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command


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
