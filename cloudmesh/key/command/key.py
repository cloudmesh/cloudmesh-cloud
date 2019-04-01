from __future__ import print_function

from pprint import pprint

from cloudmesh.common.Printer import Printer
from cloudmesh.common.parameter import Parameter
from cloudmesh.key.api.manager import Manager
from cloudmesh.management.configuration.SSHkey import SSHkey
from cloudmesh.management.configuration.config import Config
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters
from cloudmesh.shell.variables import Variables
from cloudmesh.compute.libcloud.Provider import Provider


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
             key list --cloud=CLOUDS [--output=OUTPUT]
             key list --source=ssh [--dir=DIR] [--output=OUTPUT]
             key list --source=git [--output=OUTPUT] [--username=USERNAME]
             key list [NAMES] [--output=OUTPUT]
             key load --filename=FILENAME [--output=OUTPUT]
             key add [NAME] [--source=FILENAME]
             key add [NAME] [--source=git]
             key add [NAME] [--source=ssh]
             key get NAME [--output=OUTPUT]
             key default --select
             key delete (NAMES | --select | --all) [--dryrun]
             key delete NAMES --cloud=CLOUDS [--dryrun]
             key upload [NAMES] [--cloud=CLOUDS] [--dryrun]
             key upload [NAMES] [VMS] [--dryrun]
             key group upload [--group=GROUPNAMES] [--cloud=CLOUDS] [--dryrun]
             key group add [--group=GROUPNAMES] [--cloud=CLOUDS] [--dryrun]
             key group add --file=FILENAME
             key group delete [--group=GROUPNAMES] [NAMES] [--dryrun]
             key group list [--group=GROUPNAMES] [--output=OUTPUT]
             key group export --group=GROUNAMES --filename=FILENAME


           Arguments:
             VMS            Parameterized list of virtual machines
             CLOUDS         The clouds
             NAME           The name of the key.
             SOURCE         db, ssh, all
             KEYNAME        The name of a key. For key upload it defaults to the default key name.
             OUTPUT         The format of the output (table, json, yaml)
             FILENAME       The filename with full path in which the key
                            is located

           Options:
              --dir=DIR                     the directory with keys [default: ~/.ssh]
              --output=OUTPUT               the format of the output [default: table]
              --source=SOURCE               the source for the keys [default: cm]
              --username=USERNAME           the source for the keys [default: none]
              --name=KEYNAME                The name of a key


           Description:

               Please note that some values are read from the cloudmesh4.yaml
               file. One such value is cloudmesh.profile.user

               Manages public keys is an essential component of accessing
               virtual machine sin the cloud. There are a number of sources
               where you can find public keys. This includes teh ~/.ssh
               directory and for example github. To list these keys the
               following list functions are provided.

                key list --source=git  [--username=USERNAME]
                    lists all keys in git for the specified user. If the
                    name is not specified it is read from cloudmesh4.yaml
                key list --source=ssh  [--dir=DIR] [--output=OUTPUT]
                    lists all keys in the directory. If the directory is not
                    specified the default will be ~/.ssh
                key list NAMES
                    lists all keys in the named virtual machines.

               The keys will be uploaded into cloudmesh with the add command
               under the given name. If the name is not specified the name
               cloudmesh.profile.user is assumed.

                key add --ssh
                    adds the default key in ~/.ssh/id_rsa.pub
                key add NAME  --source=FILENAME
                    adds the key specified by the filename with the given name
                key add NAME --git --username=username
                    adds a named github key from a user with the given github
                    username.

                Once the keys are uploaded to github, they can be listed

                key list [NAME] [--output=OUTPUT]
                    list the keys loaded to cloudmesh in the given format:
                    json, yaml, table. table is default. The NAME can be
                    specified and if omitted the name cloudmesh.profile.user
                    is assumed.

                key get NAME
                    Retrieves the key indicated by the NAME parameter from
                    cloudmesh and prints its details.
                key default --select
                    Select the default key interactively
                key delete NAMES
                    deletes the keys. This may also have an impact on groups
                key rename NAME NEW
                    renames the key from NAME to NEW.

               Group management of keys is an important concept in cloudmesh,
               allowing multiple users to be added to virtual machines.
               The keys must be uploaded to cloudmesh with a name so they can
               be used in a group. The --dryrun option executes the command
               without uploading the information to the clouds. If no groupname
               is specified the groupname default is assumed. If no cloudnames
               are specified, all active clouds are assumed. active clouds can be
               set in the cloudmesh4.yaml file.

                key group delete [GROUPNAMES] [NAMES] [--dryrun]
                    deletes the named keys from the named groups.

                key group list [GROUPNAMES] [--output=OUTPUT]
                    list the key names and details in the group.

                key group upload [GROUPNAMES] [CLOUDS] [--dryrun]
                    uploads the named groups to the specified clouds.

               In some cases you may want to store the public keys in files. For
               this reason we support the following commands.

                key group add --group=GROUPNAME --file=FILENAME
                    the command adds the keys to the given group. The keys are
                    written in the files in yaml format.


                key group export --group=GROUNAMES --filename=FILENAME
                    the command exports the keys to the given group. The keys are
                    written in the files in yaml format.


                The yaml format is as follows:

                cloudmesh:
                  keys:
                    NAMEOFKEY:
                      name: NAMEOFKEY
                      key: ssh-rsa AAAA..... comment
                      group:
                      - GROUPNAME
                    ...

                If a key is included in multiple groups they will be added
                to the grouplist of the key
        """

        map_parameters(arguments,
                       'cloud',
                       'output',
                       'source',
                       'dir')

        pprint(arguments)

        invalid_names = ['tbd', 'none', "", 'id_rsa']
        m = Manager()

        if arguments.list and arguments.source == "git":
            # this is much simpler
            config = Config()
            username = config["cloudmesh.profile.github"]
            print("Username:", username)
            keys = SSHkey().get_from_git(username)
            pprint(keys)
            print(Printer.flatwrite(
                keys,
                sort_keys=["name"],
                order=["id", "name", "fingerprint", "source"],
                header=["Id", "Name", "Fingerprint", "Source"])
            )

            return ""

        elif arguments.list and arguments.source == "ssh":
            # this is much simpler

            sshkey = SSHkey()
            print(Printer.flatwrite(
                [sshkey],
                sort_keys=["name"],
                order=["name", "type", "fingerprint", "comment"],
                header=["Name", "Type", "Fingerprint", "Comment"])
            )
            return ""

        elif arguments.list and arguments.cloud:

            clouds = Parameter.expand(arguments.cloud)
            print(clouds)

            if len(clouds) == 0:
                variables = Variables()
                cloudname = variables['cloud']
                clouds = [cloudname]
            cloudkey = []
            for cloud in clouds:
                print(cloud)
                provider = Provider(clouds)
                cloudkey.append(provider.keys())

            print(Printer.flatwrite(
                [cloudkey],
                sort_keys=["name"],
                order=["name", "type", "fingerprint", "comment"],
                header=["Name", "Type", "Fingerprint", "Comment"])
            )

            return ""

        elif arguments.list and arguments.source == "db":

            if arguments.NAMES:
                names = Parameter.expand(arguments.NAMES)

                print("find the keys of the following vms", names)
                print("the keys will be read from mongo")

            return ""

        return ""
