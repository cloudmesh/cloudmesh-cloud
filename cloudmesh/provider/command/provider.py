from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.variables import Variables
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.key.api.key import Key
from cloudmesh.management.configuration.SSHkey import SSHkey
from cloudmesh.management.configuration.arguments import Arguments
from cloudmesh.management.configuration.config import Config
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters
from pprint import pprint
from cloudmesh.common.util import banner
from cloudmesh.provider import ComputeProviderPlugin

class ProviderCommand(PluginCommand):

    # see https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/KeyCommand.py
    # see https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/AkeyCommand.py

    # noinspection PyUnusedLocal
    @command
    def do_provider(self, args, arguments):
        """
        ::

           Usage:
             provider list [--output=OUTPUT]
             provider delete NAME
             provider add NAME

           Arguments:
             NAME           The name of the key.

           Options:
              --output=OUTPUT               the format of the output [default: table]


           Description:

                THIS IS NOT YET IMPLEMENTED

                Managing the providers
        """

        map_parameters(arguments, 'output')

        if arguments.list:

            banner("Compute Providers")

            providers = ComputeProviderPlugin.__subclasses__()

            for provider in providers:
                print (provider.kind)
                pprint(provider)


        elif arguments.delete:
            raise NotImplementedError

        elif arguments.add:
            raise NotImplementedError

        return ""
