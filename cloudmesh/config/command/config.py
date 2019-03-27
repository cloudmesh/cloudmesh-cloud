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
             config set ATTRIBUTE=VALUE
             config verify
             config check


           Arguments:
             VMS            Para,eterized list of virtual machines
             CLOUDS         The clouds
             NAME           The name of the key.
             SOURCE         db, ssh, all
             KEYNAME        The name of a key. For key upload it defaults to the default key name.
             FORMAT         The format of the output (table, json, yaml)
             FILENAME       The filename with full path in which the key
                            is located

           Options:
              --dir=DIR                     the directory with keys [default: ~/.ssh]
              --format=FORMAT               the format of the output [default: table]
              --source=SOURCE               the source for the keys [default: cm]
              --username=USERNAME           the source for the keys [default: none]
              --name=KEYNAME                The name of a key


           Description:

             config check
                checks if the ssh key ~/.ssh/id_rsa has a password. Verifies it
                through entering the passphrase

                ssh-keygen
                ssh-add

                cms config encrypt ~/.cloudmesh/cloudmesh4.yaml
                cms config decrypt ~/.cloudmesh/cloudmesh4.yaml

        """

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

        elif arguments.verify:
            e.pem_verify()

        elif arguments.check:
            e.check_passphrase()

        elif arguments.set:

            Console.error("not implemented")
            raise NotImplementedError

        return ""
