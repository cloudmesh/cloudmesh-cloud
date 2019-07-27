import os
import sys
import shutil

import oyaml as yaml
from cloudmesh.common.FlatDict import flatten
from cloudmesh.common.Printer import Printer
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.management.configuration.config import Config
from cloudmesh.security.encrypt import EncryptFile
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters
from cloudmesh.common.util import path_expand

class ConfigCommand(PluginCommand):

    # see https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/KeyCommand.py
    # see https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/AkeyCommand.py

    # noinspection PyUnusedLocal
    @command
    def do_config(self, args, arguments):
        """
        ::

           Usage:
             config  -h | --help
             config cat [less]
             config check
             config encrypt [SOURCE] [--keep]
             config decrypt [SOURCE]
             config edit [ATTRIBUTE]
             config set ATTRIBUTE=VALUE
             config get ATTRIBUTE [--output=OUTPUT]
             config ssh keygen
             config ssh verify
             config ssh check
             config ssh pem
             config cloud verify NAME [KIND]
             config cloud edit [NAME] [KIND]
             config cloud list NAME [KIND] [--secrets]


           Arguments:
             SOURCE           the file to encrypted or decrypted.
                              an .enc is added to the filename or removed form it
                              dependent of if you encrypt or decrypt
             ATTRIBUTE=VALUE  sets the attribute with . notation in the
                              configuration file.
             ATTRIBUTE        reads the attribute from the container and sets it
                              in the configuration file
                              If the attribute is a password, * is written instead
                              of the character included

           Options:
              --name=KEYNAME     The name of a key
              --output=OUTPUT    The output format [default: yaml]
              --secrets          Print the secrets. Use carefully.

           Description:

             config check
                checks if the ssh key ~/.ssh/id_rsa has a password. Verifies it
                through entering the passphrase

             Key generation

                Keys must be generated with

                    ssh-keygen -t rsa -m pem
                    openssl rsa -in ~/.ssh/id_rsa -out ~/.ssh/id_rsa.pem

                or
                    cms config ssh keygen

                Key validity can be checked with

                    cms config check

                The key password can be verified with

                    cms config verify


                ssh-add

                cms config encrypt ~/.cloudmesh/cloudmesh4.yaml
                cms config decrypt ~/.cloudmesh/cloudmesh4.yaml


                config set ATTRIBUTE=VALUE

                    config set profile.name=Gregor


        """
        # d = Config()                #~/.cloudmesh/cloudmesh4.yaml
        # d = Config(encryted=True)   # ~/.cloudmesh/cloudmesh4.yaml.enc

        map_parameters(arguments, "keep", "secrets", "output")

        source = arguments.SOURCE or path_expand("~/.cloudmesh/cloudmesh4.yaml")
        destination = source + ".enc"

        if arguments.cloud and arguments.edit and arguments.NAME is None:
            path = path_expand("~/.cloudmesh/cloudmesh4.yaml")
            print(path)
            Shell.edit(path)
            return ""

        cloud = arguments.NAME
        kind = arguments.KIND
        if kind is None:
            kind = "cloud"

        configuration = Config()



        if arguments.cloud and arguments.verify:
            service = configuration[f"cloudmesh.{kind}.{cloud}"]

            result = {"cloudmesh": {"cloud": {cloud: service}}}

            action = "verify"
            banner(
                f"{action} cloudmesh.{kind}.{cloud} in ~/.cloudmesh/cloudmesh4.yaml")

            print(yaml.dump(result))

            flat = flatten(service, sep=".")

            for attribute in flat:
                if "TBD" in str(flat[attribute]):
                    Console.error(
                        f"~/.cloudmesh4.yaml: Attribute cloudmesh.{cloud}.{attribute} contains TBD")

        elif arguments.cloud and arguments.list:
            service = configuration[f"cloudmesh.{kind}.{cloud}"]
            result = {"cloudmesh": {"cloud": {cloud: service}}}

            action = "list"
            banner(
                f"{action} cloudmesh.{kind}.{cloud} in ~/.cloudmesh/cloudmesh4.yaml")

            lines = yaml.dump(result).split("\n")
            secrets = not arguments.secrets
            result = Config.cat_lines(lines, mask_secrets=secrets)
            print (result)

        elif arguments.cloud and arguments.edit:

            #
            # there is a duplicated code in config.py for this
            #
            action = "edit"
            banner(
                f"{action} cloudmesh.{kind}.{cloud}.credentials in ~/.cloudmesh/cloudmesh4.yaml")

            credentials = configuration[f"cloudmesh.{kind}.{cloud}.credentials"]

            print(yaml.dump(credentials))

            for attribute in credentials:
                if "TBD" in credentials[str(attribute)]:
                    value = credentials[attribute]
                    result = input(f"Please enter {attribute}[{value}]: ")
                    credentials[attribute] = result

            # configuration[f"cloudmesh.{kind}.{cloud}.credentials"] = credentials

            print(yaml.dump(
                configuration[f"cloudmesh.{kind}.{cloud}.credentials"]))

        elif arguments["edit"] and arguments["ATTRIBUTE"]:

            attribute = arguments.ATTRIBUTE

            config = Config()

            config.edit(attribute)

            config.save()

            return ""


        elif arguments.cat:

            content = Config.cat()

            import shutil
            columns, rows = shutil.get_terminal_size(fallback=(80, 24))

            lines = content.split("\n")

            counter = 1
            for line in lines:
                if arguments.less:
                    if  counter % (rows-2) == 0:
                        x = input().split("\n")[0].strip()
                        if x !='' and x in 'qQxX' :
                            return ""
                print (line)
                counter += 1

            return ""

        elif arguments.check and not arguments.ssh:

            Config.check()

        elif arguments.encrypt:

            e = EncryptFile(source, destination)

            e.encrypt()
            Console.ok(f"{source} --> {destination}")
            if not arguments.keep:
                os.remove(source)

            Console.ok("file encrypted")

            return ""

        elif arguments.decrypt:

            if ".enc" not in source:
                source = source + ".enc"
            else:
                destination = source.replace(".enc", "")

            if not os.path.exists(source):
                Console.error(f"encrypted file {source} does not exist")
                sys.exit(1)

            if os.path.exists(destination):
                Console.error(
                    f"decrypted file {destination} does already exist")
                sys.exit(1)

            e = EncryptFile(source, destination)

            e.decrypt(source)
            Console.ok(f"{source} --> {source}")

            Console.ok("file decrypted")
            return ""

        elif arguments.ssh and arguments.verify:

            e = EncryptFile(source, destination)

            e.pem_verify()

        elif arguments.ssh and arguments.check:

            e = EncryptFile(source, destination)

            key = path_expand("~/.ssh/id_rsa")
            r = e.check_key(key)
            if r:
                Console.ok(f"Key {key} is valid")
            # does not work as it does not change it to pem format
            # e.check_passphrase()

        elif arguments.ssh and arguments.pem:

            e = EncryptFile(source, destination)

            r = e.pem_create()

        elif arguments.set:

            line = arguments["ATTRIBUTE=VALUE"]
            attribute, value = line.split("=", 1)

            if not attribute.startswith("cloudmesh."):
                attribute = f"cloudmesh.{attribute}"

            config = Config()
            config[attribute] = value
            config.save()

        elif arguments.get:

            attribute = arguments.ATTRIBUTE
            if not attribute.startswith("cloudmesh."):
                attribute = f"cloudmesh.{attribute}"

            config = Config()
            value = config[attribute]

            if type(value) == dict:
                print(Printer.write(value, output=arguments.output))
            else:
                print(f"{attribute}={value}")

        elif arguments.ssh and arguments.keygen:

            e = EncryptFile(source, destination)

            e.ssh_keygen()



        return ""
