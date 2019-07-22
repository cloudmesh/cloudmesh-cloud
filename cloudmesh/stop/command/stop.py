from cloudmesh.mongo.MongoDBController import MongoDBController
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command


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
