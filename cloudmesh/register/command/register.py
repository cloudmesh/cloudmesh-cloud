import json
from pprint import pprint
from textwrap import dedent

from cloudmesh.common.console import Console
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.register.Entry import Entry
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters
from cloudmesh.register.Register import Register
from cloudmesh.common.debug import VERBOSE

class RegisterCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_register(self, args, arguments):
        """
        ::

            Usage:
                register --cloud=CLOUD [--service=SERVICE] [--name=NAME] [--filename=FILENAME] [--keep] [ATTRIBUTES...] [--dryrun]

                This command adds the registration information in the cloudmesh
                yaml file. A FILENAME can be passed along that contains
                credential information downloaded from the cloud. The
                permissions of the FILENAME will also be changed. A y/n question
                will be asked if the file with the FILENAME should be deleted
                after integration. THis helps that all credential information
                could be managed with the cloudmesh.yaml file.

            Arguments:
                FILENAME    a filename in which the cloud credentials are stored
                ATTRIBUTES  Attribute list to replace if json file is not provided.
                            Note: Attributes will override the values from file
                            if both are used.

            Options:
                --keep               keeps the file with the filename.
                --dryrun             option to just display the formatted sample without
                                     updating the cloudmesh.yaml file.
                --filename=FILENAME  json filename containing the details to be replaced
                --cloud=CLOUD        cloud provider e.g. aws, google, openstack, oracle etc.
                --service=SERVICE    service type e.g. storage, compute, volume
                --name=NAME          name for the new registration

            Examples:

                cms register google compute --name=west_region \
                    filename=~/.cloudmesh/google.json project_id=west1 \
                    client_email=example@gmail.com

                  In the last example the values for filename, project_id, and
                  client_email will be changed to respective values from google
                  compute sample. We assume you have downloaded the credentials
                  form google and stored it in the file ~/.cloudmesh/google.json

        """


        map_parameters(arguments,
                       'cloud',
                       'service',
                       'dryrun',
                       'keep',
                       'filename',
                       'name')

        VERBOSE(arguments)

        service = arguments.service or "cloud"
        kind = arguments.cloud
        entry_name = arguments.name or arguments.cloud

        """
        TODO: Check if this is required.
        if arguments.aws and arguments.yaml:

            AWSReg = importlib.import_module(
                "cloudmesh.register.AWSRegister")
            AWSregisterer = AWSReg.AWSRegister()
            AWSregisterer.register()

        elif arguments.azure:
            if arguments.yaml:
                Registry = importlib.import_module(
                    "cloudmesh.register.AzRegister")
                AZregisterer = Registry.AzRegister()
                AZregisterer.register()

            return ""
        """


        provider = Register.get_provider(service=service, kind=kind)


        if provider is None:
            return

        if not arguments.ATTRIBUTES:
            if arguments.filename is None:
                raise ValueError("Either filename or attributes is required.")

            # Load JSON File.
            path = path_expand(arguments.filename)
            with open(path, "r") as file:
                attributes = []
                json_content = json.load(file)
                for item in json_content:
                    attributes.append(f"{item}={json_content[item]}")

            # Add the filename to attributes
            attributes.append(f"filename={arguments.filename}")
        else:
            # Use Arguments.
            attributes = arguments.ATTRIBUTES

        sample = Register.get_sample(provider,
                                     kind,
                                     cloud,
                                     entry_name,
                                     attributes)

        if arguments.dryrun:
            # Just print the value
            pprint(dedent(sample))
        else:
            # Add the entry into cloudmesh.yaml file.
            Entry.add(entry=sample,
                      base=f"cloudmesh.{sample}",
                      path="~/.cloudmesh/cloudmesh.yaml")

        Console.ok(
            f"Registered {cloud} service for {kind}"
            f" provider with name {entry_name}.")
        return ""


