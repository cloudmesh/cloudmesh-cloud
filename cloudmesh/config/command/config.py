import os
import sys

from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from cloudmesh.management.configuration.config import Config
from cloudmesh.security.encrypt import EncryptFile
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command


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
             config encrypt [SOURCE] [--keep]
             config decrypt [SOURCE]
             config edit [ATTRIBUTE]
             config set ATTRIBUTE=VALUE
             config get ATTRIBUTE [--format=FORMAT]
             config ssh keygen
             config ssh verify
             config ssh check
             config ssh pem

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
              --name=KEYNAME                The name of a key
              --format=FORMAT     The output format [default: yaml]


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

        source = arguments.SOURCE or path_expand("~/.cloudmesh/cloudmesh4.yaml")
        destination = source + ".enc"

        arguments.keep = arguments["--keep"]
        # VERBOSE(arguments)

        e = EncryptFile(source, destination)

        if arguments["edit"] and arguments["ATTRIBUTE"]:

            attribute = arguments.ATTRIBUTE

            config = Config()

            config.edit(attribute)

            config.save()

            return ""

        elif arguments.encrypt:

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
                Console.error(f"decrypted file {destination} does already exist")
                sys.exit(1)

            e.decrypt(source)
            Console.ok(f"{source} --> {source}")

            Console.ok("file decrypted")
            return ""

        elif arguments.ssh and arguments.verify:
            e.pem_verify()

        elif arguments.ssh and arguments.check:
            key = "~/.ssh/id_rsa"
            r = e.check_key(key)
            if r:
                Console.ok(f"Key {key} is valid")
            # does not work as it does not change it to pem format
            # e.check_passphrase()

        elif arguments.ssh and arguments.pem:

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

            output = arguments["--format"]
            if type(value) == dict:
                print(Printer.write(value, output=output))
            else:
                print(f"{attribute}={value}")

        elif arguments.ssh and arguments.keygen:

            e.ssh_keygen()

        return ""
