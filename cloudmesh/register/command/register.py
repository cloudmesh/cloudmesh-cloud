import json
from pprint import pprint
from textwrap import dedent

from cloudmesh.common.console import Console
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.register.Entry import Entry
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters

class RegisterCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_register(self, args, arguments):
        """
        ::

            Usage:
                register --cloud=CLOUD --service=SERVICE [--name=NAME] [--filename=FILENAME] [--keep] [ATTRIBUTES...] [--dryrun]
                register CLOUD SERVICE [--name=NAME] [--filename=FILENAME] [--keep] [ATTRIBUTES...] [--dryrun]

                This command adds the registration information in the cloudmesh
                yaml file. The permissions of the FILENAME will also be changed.
                A y/n question will be asked if the files with the filename should
                be deleted after integration.

            Arguments:
                CLOUD       cloud provider e.g. aws, google, openstack, oracle etc.
                SERVICE     service type e.g. storage, compute etc.
                FILENAME    a filename in which the cloud credentials are stored
                ATTRIBUTES  Attribute list to replace if json file is not provided.
                            Note: Attributes will override the values from file
                            if both are used.

            Options:
                --keep              keeps the file with the filename.
                --dryrun            option to just display the formatted sample without
                                    updating the cloudmesh.yaml file.
                --filename=FILENAME json filename containing the details to be replaced
                --cloud=CLOUD       cloud provider e.g. aws, google, openstack, oracle etc.
                --service=SERVICE   service type e.g. storage, compute etc.
                --name=NAME         name for the new registration

            Examples:

                cms register google compute --name=west_region filename=~/.cloudmesh/google_west.json project_id=west1 client_email=example@gmail.com

                 In the last example the values for filename, project_id, and
                 client_email will be changed to respective values from google
                 compute sample.

        """

        map_parameters(arguments,
                       'cloud',
                       'service',
                       'dryrun',
                       'keep',
                       'filename',
                       'name')

        kind = arguments.cloud
        service = arguments.service
        entry_name = kind

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


        # Extract arguments.
        if kind is None:
            kind = arguments.CLOUD

        if service is None:
            service = arguments.SERVICE

        if arguments.name is not None:
            entry_name = arguments.name

        provider = self.get_provider(service, kind)

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

        sample = self.prepare_sample(provider, kind, service, entry_name,
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
            f"Registered {service} service for {kind} provider with name {entry_name}.")
        return ""

    def get_provider(self, service, kind):
        """
        Method to import the provider based on the service and kind.
        :param service: Type of the service e.g. compute or storage etc.
        :param kind: Name of the cloud e.g. google, azure, aws etc.
        :return: Provider class
        """
        if service == 'compute' or service == 'cloud':
            if kind == 'openstack':
                from cloudmesh.openstack.compute.Provider import Provider
            elif kind == 'azure':
                banner("Azure")
                from cloudmesh.azure.compute.Provider import Provider
            elif kind == 'aws':
                from cloudmesh.aws.compute.Provider import Provider
            elif kind == 'oracle':
                from cloudmesh.oracle.compute.Provider import Provider
            elif kind == 'google':
                from cloudmesh.google.compute.Provider import Provider
            else:
                Console.error(
                    f"No suitable provider found for {kind} and {service}")
                return None
        elif service == 'storage':
            if kind == 'openstack':
                from cloudmesh.openstack.storage.Provider import Provider
            elif kind == 'azure':
                from cloudmesh.storage.azure.Provider import Provider
            elif kind == 'aws':
                from cloudmesh.storage.aws.Provider import Provider
            elif kind == 'oracle':
                from cloudmesh.oracle.compute.Provider import Provider
            elif kind == 'google':
                from cloudmesh.google.storage.Provider import Provider
            else:
                Console.error(
                    f"No suitable provider found for {kind} and {service}")
                return None
        else:
            Console.error(f"Invalid {service} provided.")
            return None

        p = Provider

        return p

    def prepare_sample(self, provider, kind, service, name, attributes):

        # Default replacements.
        replacements = {'name': name,
                        'service': service,
                        "kind": kind}

        # Add the attributes to the dict.
        for attribute in attributes:
            key, value = attribute.split("=")
            replacements[key] = value

        # Extract the sample from Provider.
        sample = provider.sample

        try:
            # Format the sample by replacing the attributes.
            sample = sample.format(**replacements)

        except KeyError as e:
            Console.error(f"Value for {e} is not specified")
            sample = None

        return sample
