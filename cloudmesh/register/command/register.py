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
                register list --cloud=CLOUD [--service=SERVICE]
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
        TODO: This is a special register allowing to use the web interface 
        to get the aws json file.
        
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

        if arguments["list"]:

            sample = provider.sample

            if len(sample) >= 1:
                Console.info(f"Sample for service={service} kind={kind}")

                print(dedent(sample))

                Console.error("The following attributes are not defined")
                print()
                keys = Register.get_sample_variables(sample)

                print("    " + "\n    ".join(sorted(keys)))
                print()

            return ""

        if provider is None:
            return

        attributes = {}

        if arguments.filename:
            # Load JSON File.
            path = path_expand(arguments.filename)
            with open(path, "r") as file:
                attributes = json.load(file)

            # Add the filename to attributes
            attributes["filename"] = arguments.filename

        if arguments.ATTRIBUTES:

            atts = arguments.ATTRIBUTES
            for attribute in atts:
                key, value = attribute.split("=", 1)
                attributes[key] = value

        VERBOSE(attributes)

        sample = Register.get_sample(provider,
                                     kind,
                                     service,
                                     entry_name,
                                     attributes)

        if sample is None:
            Console.error("The sample is not fully filled out.")
            return ""

        if arguments.dryrun:
            # Just print the value
            pprint(dedent(sample))
        else:
            # Add the entry into cloudmesh.yaml file.
            Entry.add(entry=sample,
                      base=f"cloudmesh.{sample}",
                      path="~/.cloudmesh/cloudmesh.yaml")

        Console.ok(
            f"Registered {service} service for {kind}"
            f" provider with name {entry_name}.")
        return ""
