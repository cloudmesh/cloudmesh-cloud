from cloudmesh.common.console import Console
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.management.configuration.config import Config
from pprint import pprint
from cloudmesh.common.FlatDict import flatten
import oyaml as yaml
from cloudmesh.common.util import banner
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand


class YamlCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_yaml(self, args, arguments):
        """
        ::

          Usage:
                yaml verify NAME [KIND]
                yaml edit [NAME] [KIND]
                yaml list NAME [KIND]


          This verifies the cloudmesh4.yaml file

          Arguments:
              NAME   the name of the service in the YAML file
              KIND   the kind of the cloud service such as cloud, storage [default=cloud]

          Description:

             verify cloud chameleon


        """

        if arguments.edit and arguments.NAME is None:

            path = path_expand("~/.cloudmesh/cloudmesh4.yaml")
            print (path)
            Shell.edit(path)
            return ""


        cloud = arguments.NAME
        kind = arguments.KIND
        if kind is None:
            kind = "cloud"

        configuration = Config()


        if arguments.verify:
            service = configuration[f"cloudmesh.{kind}.{cloud}"]

            result = {"cloudmesh": {"cloud": {cloud: service}}}

            action = "verify"
            banner(f"{action} cloudmesh.{kind}.{cloud} in ~/.cloudmesh/cloudmesh4.yaml")

            print (yaml.dump(result))

            flat = flatten(service, sep=".")

            for attribute in flat:
                if "TBD" in str(flat[attribute]):
                    Console.error(f"~/.cloudmesh4.yaml: Attribute cloudmesh.{cloud}.{attribute} contains TBD")

        elif arguments.list:
            service = configuration[f"cloudmesh.{kind}.{cloud}"]
            result = {"cloudmesh": {"cloud": {cloud: service}}}

            action = "verify"
            banner(f"{action} cloudmesh.{kind}.{cloud} in ~/.cloudmesh/cloudmesh4.yaml")

            print (yaml.dump(result))

        elif arguments.edit:

            #
            # there is a duplicated code in config.py for this
            #
            action = "edit"
            banner(f"{action} cloudmesh.{kind}.{cloud}.credentials in ~/.cloudmesh/cloudmesh4.yaml")

            credentials = configuration[f"cloudmesh.{kind}.{cloud}.credentials"]

            print (yaml.dump(credentials))

            for attribute in credentials:
                if "TBD" in credentials[str(attribute)]:
                    value = credentials[attribute]
                    result = input(f"Please enter {attribute}[{value}]: ")
                    credentials[attribute] = result

            #configuration[f"cloudmesh.{kind}.{cloud}.credentials"] = credentials

            print(yaml.dump(configuration[f"cloudmesh.{kind}.{cloud}.credentials"] ))

        return ""
