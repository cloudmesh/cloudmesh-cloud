from __future__ import print_function

from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command


class KeyCommand(PluginCommand):

    # see https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/KeyCommand.py
    # see https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/AkeyCommand.py

    # noinspection PyUnusedLocal
    @command
    def do_key(self, args, arguments):
        """
        ::

           Usage:
             key  -h | --help
             key list --cloud=CLOUD
             key list --source=db [--format=FORMAT]
             key list --source=yaml [--format=FORMAT]
             key list --source=ssh [--dir=DIR] [--format=FORMAT]
             key list --source=git [--format=FORMAT] [--username=USERNAME]
             key list
             key load [--format=FORMAT]
             key add [NAME] [--source=FILENAME]
             key add [NAME] [--git]
             key add [NAME] [--ssh]
             key get NAME
             key default --select
             key delete (NAME | --select | --all)
             key delete NAME --cloud=CLOUD
             key upload [NAME] [--cloud=CLOUD]
             key upload [NAME] --active
           Manages the keys
           Arguments:
             CLOUD          The cloud
             NAME           The name of the key.
             SOURCE         db, ssh, all
             KEYNAME        The name of a key. For key upload it defaults to the default key name.
             FORMAT         The format of the output (table, json, yaml)
             FILENAME       The filename with full path in which the key
                            is located
             NAME_ON_CLOUD  Typically the name of the keypair on the cloud.
           Options:
              --dir=DIR                     the directory with keys [default: ~/.ssh]
              --format=FORMAT               the format of the output [default: table]
              --source=SOURCE               the source for the keys [default: db]
              --username=USERNAME           the source for the keys [default: none]
              --name=KEYNAME                The name of a key
              --all                         delete all keys
              --force                       delete the key form the cloud
              --name_on_cloud=NAME_ON_CLOUD Typically the name of the keypair on the cloud.
           Description:
           key list --source=git  [--username=USERNAME]
              lists all keys in git for the specified user. If the
              name is not specified it is read from cloudmesh.yaml
           key list --source=ssh  [--dir=DIR] [--format=FORMAT]
              lists all keys in the directory. If the directory is not
              specified the default will be ~/.ssh
           key list --source=yaml  [--dir=DIR] [--format=FORMAT]
              lists all keys in cloudmesh.yaml file in the specified directory.
               dir is by default ~/.cloudmesh
           key list [--format=FORMAT]
               list the keys in the giiven format: json, yaml,
               table. table is default
           key list
                Prints list of keys. NAME of the key can be specified
           key add ssh
               adds the default key with the name id_rsa.pub
           key add NAME  --source=FILENAME
               adds the key specifid by the filename to the key
               database
           key get NAME
               Retrieves the key indicated by the NAME parameter from database
               and prints its fingerprint.
           key default --select
                Select the default key interactively
           key delete NAME
                deletes a key. In yaml mode it can delete only key that
                are not saved in the database
           key rename NAME NEW
                renames the key from NAME to NEW.

        """

        print(arguments)

        # m = Manager()

        # if arguments.FILE:
        #    print("option a")
        #    m.list(arguments.FILE)

        # elif arguments.list:
        #    print("option b")
        #    m.list("just calling list without parameter")
