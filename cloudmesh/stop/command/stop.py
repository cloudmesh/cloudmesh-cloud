from cloudmesh.mongo.MongoDBController import MongoDBController
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.common.console import Console


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
        if MongoDBController().service_is_running():
            MongoDBController().stop()
        else:
            Console.ok("MongoDB service is already stopped")
