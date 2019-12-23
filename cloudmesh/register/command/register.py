from pprint import pprint

from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import banner
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


                1. If either file is found in `~/Downloads`, it is moved to
                   `~/.cloudmesh` and the permissions are changed
                2. If such a file already exists there it will ask if it should
                   be overwritten in case the content is not the same
                3. The content of the file will be read to determine if it is
                   likely to be an AWS credential
                4. The credential will be added to the cloudmesh yaml file

            Azure (TODO: THIS HAS TO BE IMPLEMENTED)

                To use this command you must have an Azure account and Azure CLI
                installed. Mote deatils to this can be found at:

                   TBD: include link

                This command leverages the Azure CLI to extract specific account
                parameters and update the `cloudmesh.yaml` configuration file.

                1. When this command is run, the `az login` Azure CLI command is
                   executed, prompting you to login to your azure account via
                   your default browser, which should then redirect you back to
                   your CLI.

                2. The azure cli command for `az account show` is then
                   referenced to pull the account's subscription id and tenant
                   id.

                3. Run the command

                        `az ad sp create-for-rbac --name http://cloudmesh`

                   to reference the application id and secret key.

                   NOTE: If there is already a secret key reference in the
                   `cloudmesh.yaml` file, it will be rendered useless once the new
                   secret key is obtained; requiring you to ensure the key has
                   been successfully applied in the next step to the
                   configuration file and cms init is called.

                4. The credentials will be added to the
                   `~/.cloudmesh.yaml` configuration file.

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

                A new cloud can be added to the existing cloudmesh.yaml file
                with thsi command. AN example is

                cms register -v  compute aws ABC \
                    region=one \
                    EC2_ACCESS_ID=TBD
                    EC2_SECRET_KEY=TBD
                    EC2_SECRET_KEY=TBD

                This command can also be used to overwrite an existing entry

        """

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

        elif arguments.google:

            from cloudmesh.google.storage.Provider import Provider

            banner("Read the  specification from json and write to yaml file")
            path = path_expand(
                arguments.FILE_JSON or "~/.cloudmesh/google.json")

            name = arguments.storage or "google"
            Provider.json_to_yaml(name, filename=path)

            Console.error("deleting {path} not implemented")
            return ""

        elif arguments.chameleon:

            Console.error("not yet implemented")
            return ""


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

            elif kind == "storage" and service == "google":
                from cloudmesh.google.storage.Provider import Provider

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

            elif kind == "storage" and service == "google":
                from cloudmesh.google.storage.Provider import Provider

            else:
                Console.error("The provider {google} for {kind}"
                              " does not have a sample configuration")
                return ""

            if kind in ["compute", "cloud"]:
                kind = "cloud"
            if kind in ["storage"]:
                kind = "storage"
            else:
                Console.error("the kind {kind} is not supported")
                return ""


            sample = Provider.sample

            try:
                sample = sample.format(**replacements)

                if arguments["-v"]:
                    print (sample)


                Entry.add(entry=sample,
                        base=f"cloudmesh.{kind}",
                        path="~/.cloudmesh/cloudmesh.yaml")

            except KeyError as e:
                Console.error(f"Value for {e} is not specified")
            print (dedent(sample))


        return ""
