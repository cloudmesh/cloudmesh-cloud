from __future__ import print_function
from pprint import pprint
import os
from cloudmesh.security.encrypt import EncryptFile
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.common.util import path_expand
from cloudmesh.terminal.Terminal import VERBOSE
from cloudmesh.common.console import Console


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
             config encrypt [SOURCE]
             config decrypt [SOURCE]
             config edit [SOURCE]
             config set ATTRIBUTE=VALUE
             config set ATTRIBUTE
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
             ATTRIBUTE        reads the attribute from the terminal and sets it
                              in the configuration file
                              If the attribute is a password, * is written instead
                              of the character included

           Options:
              --name=KEYNAME                The name of a key


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

        arguments.SOURCE = arguments.SOURCE or \
                           path_expand("~/.cloudmesh/cloudmesh4.yaml")
        arguments.DESTINATION = arguments.SOURCE + ".enc"

        VERBOSE.print(arguments, verbose=9)

        e = EncryptFile(arguments.SOURCE, arguments.DESTINATION)

        if arguments.encrypt:

            e.encrypt()
            Console.ok("{SOURCE} --> {DESTINATION}".format(**arguments))
            Console.ok("file encrypted")
            return ""

        elif arguments.decrypt:
            # if the file is existed
            if not os.path.exists(arguments.DESTINATION):
                Console.error(
                    "encrypted file {DESTINATION} does not exist".format(
                        **arguments))

            e.decrypt(arguments.SOURCE, arguments.DESTINATION)
            Console.ok("{DESTINATION} --> {SOURCE}".format(**arguments))

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

            Console.error("not implemented")
            raise NotImplementedError

        elif arguments.ssh and arguments.keygen:

            e.ssh_keygen()

        return ""
