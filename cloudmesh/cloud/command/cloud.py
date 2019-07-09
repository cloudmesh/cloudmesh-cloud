from cloudmesh.common.console import Console
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.management.configuration.config import Config
from pprint import pprint
from cloudmesh.common.FlatDict import flatten
import oyaml as yaml
from cloudmesh.common.util import banner

class CloudCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_cloud(self, args, arguments):
        """
        ::

          Usage:
                verify NAME [KIND]

          This verifies the cloudmesh4.yaml file

          Arguments:
              NAME   the name of the service in the YAML file
              KIND   the kind of the cloud service such as cloud, storage [default=cloud]

          Description:

             verify cloud chameleon


        """
        cloud = arguments.NAME
        kind = arguments.kind
        if arguments.KIND is None:
            kind = "cloud"

        configuration = Config()[f"cloudmesh.{kind}.{cloud}"]

        result = {"cloudmesh": {"cloud": {cloud: configuration}}}

        banner(f"checking cloudmesh.{kind}.{cloud} in ~/.cloudmesh/cloudmesh4.yaml file")

        print (yaml.dump(result))

        flat = flatten(configuration, sep=".")

        for attribute in flat:
            if "TBD" in str(flat[attribute]):
                Console.error(f"~/.cloudmesh4.yaml: Attribute cloudmesh.{cloud}.{attribute} contains TBD")

        return ""
