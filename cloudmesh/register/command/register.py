from pprint import pprint

from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
import importlib
from cloudmesh.register.Entry import Entry
from textwrap import dedent

class RegisterCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_register(self, args, arguments):
        """
        ::

          Usage:
              register aws yaml
              register aws [FILENAME] [--keep]
              register azure [FILENAME] [--keep]
              register google [FILENAME] [--keep]
              register chameleon [FILENAME] [--keep]
              register new [-v] KIND SERVICE NAME [ATTRIBUTES...]
              register list KIND SERVICE NAME [ATTRIBUTES...]


          This command adds the registration information the th cloudmesh
          yaml file. The permissions of theFILENAME will also be changed.
          A y/n question will be asked if the files with the filename should
          be deleted after integration

          Arguments:
              FILENAME   a filename in which the cloud credentials are stored

          Options:
              --keep    keeps the file with the filename.

          Description:

            AWS

                AWS dependent on how you downloaded the credentials will either
                use the filename `credentials.csv` or `accessKey.csv`

                Our command is smart provides some convenience functionality.


                1. If either file is found in ~/Downloads, it is moved to
                   ~/.cloudmesh and the permissions are changed
                2. If such a file already exists there it will ask if it should
                   be overwritten in case the content is not the same
                3. The content of the file will be read to determine if it is
                   likely to be an AWS credential
                4. The credential will be added to the cloudmesh yaml file

            Azure

                Is not yet implemented

            Google

                Is not yet implemented

            Chameleon Cloud

                is not yet implemented

          Register from template:

            register list KIND SERVICE NAME [ATTRIBUTES...]

                This command lists the template for a provider and fills it out
                with the attributes. It can be used to check what information
                would be added with the new command. The template is included in
                the Provider itself. Leaving the attributes off, just prints the
                template

                Examples:

                    cms register list compute openstack ABC
                    cms register list compute openstack ABC uri=TBD tenant=TBD region=TBD

                    In the last example the values for uri, tennant, and region
                    will be cahnged to TBD

            register new KIND SERVICE NAME ATTRIBUTES...



        """

        if arguments.aws:
            # Pandas should not be used, but
            # TODO: change csv
            # import csv
            # the csv code needs to be changed

            if arguments.yaml:
                AWSReg = importlib.import_module(
                    "cloudmesh.register.AWSRegister")
                AWSregisterer = AWSReg.AWSRegister()
                AWSregisterer.register()

            else:
                Console.error("not yet implemented")

        elif arguments.azure:
            Console.error("not yet implemented")

        elif arguments.google:

            Console.error("not yet implemented")

        elif arguments.chameleon:

            Console.error("not yet implemented")

        elif arguments.list:

            kind = arguments.KIND
            service = arguments.SERVICE
            attributes = arguments.ATTRIBUTES
            name = arguments.NAME

            replacements = {'name': name,
                            'service': service}
            for attribute in attributes:
                key, value = attribute.split("=")
                replacements[key] = value

            if kind == "compute" and service == "openstack":
                from cloudmesh.compute.openstack.Provider import Provider

            elif kind == "compute" and service == "azure":
                from cloudmesh.compute.azure.Provider import Provider

            elif kind == "compute" and service == "aws":
                from cloudmesh.compute.aws.Provider import Provider

            elif kind == "compute" and service == "oracle":
                from cloudmesh.oracle.compute.Provider import Provider

            sample = Provider.sample


            try:
                if len(attributes) > 0:
                    sample = sample.format(**replacements)
            except KeyError as e:
                Console.error(f"Value for {e} is not specified")
            print (dedent(sample))

        elif arguments.new:

            kind = arguments.KIND
            service = arguments.SERVICE
            attributes = arguments.ATTRIBUTES
            name = arguments.NAME

            replacements = {'name': name,
                            'service': service}
            for attribute in attributes:
                key, value = attribute.split("=")
                replacements[key] = value

            if kind == "compute" and service == "openstack":
                from cloudmesh.compute.openstack.Provider import Provider

            elif kind == "compute" and service == "azure":
                from cloudmesh.compute.azure.Provider import Provider

            elif kind == "compute" and service == "aws":
                from cloudmesh.compute.aws.Provider import Provider

            elif kind == "compute" and service == "oracle":
                from cloudmesh.oracle.compute.Provider import Provider

            sample = Provider.sample

            try:
                sample = sample.format(**replacements)

                if arguments["-v"]:
                    print (sample)

                Entry.add(entry=sample,
                        base="cloudmesh.cloud",
                        path="~/.cloudmesh/cloudmesh.yaml")


            except KeyError as e:
                Console.error(f"Value for {e} is not specified")
            print (dedent(sample))


        return ""
