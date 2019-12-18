from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.variables import Variables
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.key.Key import Key
from cloudmesh.management.configuration.SSHkey import SSHkey
from cloudmesh.management.configuration.arguments import Arguments
from cloudmesh.configuration.Config import Config
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters
from cloudmesh.configuration.security.encrypt import KeyHandler
from cloudmesh.common.util import path_expand, yn_choice
from pprint import pprint
import os
import sys


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
             key list [--output=OUTPUT]
             key init
             key add NAME --filename=FILENAME [--output=OUTPUT]
             key add [NAME] [--source=FILENAME]
             key add [NAME] [--source=git]
             key add [NAME] [--source=ssh]
             key delete NAMES [--cloud=CLOUDS] [--dryrun]
             key upload [NAMES] [--cloud=CLOUDS] [--dryrun]
             key upload [NAMES] [VMS] [--dryrun]
             key group upload [NAMES] [--group=GROUPNAMES] [--cloud=CLOUDS] [--dryrun]
             key group add [NAMES] [--group=GROUPNAMES] [--cloud=CLOUDS] [--dryrun]
             key group delete [--group=GROUPNAMES] [NAMES] [--dryrun]
             key group list [--group=GROUPNAMES] [--output=OUTPUT]
             key group export --group=GROUNAMES --filename=FILENAME
             key gen (ssh | pem) [--filename=FILENAME] [--nopass] [--set_path] [--force]
             key reformat (ssh | pem) [--filename=FILENAME] [--format=FORMAT]
                                      [--nopass] [--pub]
             key verify (ssh | pem) [--filename=FILENAME] [--pub] [--check_pass]

           Arguments:
             VMS        Parameterized list of virtual machines
             CLOUDS     The clouds
             NAME       The name of the key.
             SOURCE     db, ssh, all
             OUTPUT     The format of the output (table, json, yaml)
             FILENAME   The filename with full path in which the key is located
             FORMAT     Desired key format (SubjectInfo, SSH, OpenSSL, PKCS8)

           Options:
              --dir=DIR             the directory with keys [default: ~/.ssh]
              --check_pass          Flag where program query user for password
              --filename=FILENAME   the name and full path to the file
              --nopass              Flag indicating if the key has no password
              --output=OUTPUT       the format of the output [default: table]
              --pub                 Indicates that the public key is passed in
              --set_path            Sets the cloudmesh encryption key path to
                                    the full path of the generated keys
              --source=SOURCE       the source for the keys
              --username=USERNAME   the source for the keys [default: none]


           Description:

               Please note that some values are read from the cloudmesh.yaml
               file. One such value is cloudmesh.profile.user

               Management of public keys is an essential component of accessing
               virtual machines in the cloud. There are a number of sources
               where you can find public keys. This includes the ~/.ssh
               directory and for example github. If you do not already have a
               public-private key pair they can be generated using cloudmesh

               key gen ssh 
                   This will create the public-private keypair of ~/.ssh/id_rsa
                   and ~/.ssh/id_rsa.pub in OpenSSH format

               key gen pem 
                   This will create the public-private keypair of ~/.ssh/id_rsa
                   and ~/.ssh/id_rsa.pub in PEM format

               key gen (ssh | pem) --filename=~/.cloudmesh/foobar
                   This will generate the public-private key pair of 
                   ~/.cloudmesh/foobar and ~/.cloudmesh/foobar.pub

               key gen (ssh | pem) --filename=~/.cloudmesh/foobar --set_path
                   This will generate the keys as stated above, but it will
                   also set cloudmesh to use these keys for encryption.

               Keys can also be verified for their formatting and passwords.
               By default cloudmesh checks ~/.ssh/id_rsa and ~/.ssh/id_rsa.pub
               If the key is password protected the formatting can only be
               verified if the password is provided (--check_pass argument)

               key verify pem
                   Verifies that ~/.ssh/id_rsa has PEM format

               key verify ssh --pub
                   Verifies that ~/.ssh/id_rsa.pub has OpenSSH format

               key verify pem --filename=~/.cloudmesh/foobar
                   Verifies if the private key located at ~/.cloudmesh/foobar
                   is password protected

               key verify pem --filenam=~/.cloudmesh/foobar --check_pass
                   Request the password to the file, then checks if the
                   key is in proper PEM format

               You may find the need to keep the values of your keys but
               different encodings or formats. These aspects of your key can
               also be changed using cloudmesh.

               key reformat pem
                   Will reformat the ~/.id_rsa.pub key from PEM to OpenSSH

               key reformat ssh
                   Will reformat the ~/.id_rsa.pub key from OpenSSH to PEM

               key reformat --filename=~/.id_rsa --format=PKCS8
                   Will reformat the private key to PKCS8 format

               Keys will be uploaded into cloudmesh database with the add
               command under the given NAME. If the name is not specified the name
               cloudmesh.profile.user is assumed.

                key add NAME  --source=ssh
                    adds the default key in ~/.ssh/id_rsa.pub
                key add NAME  --source=FILENAME
                    adds the key specified by the filename with the given name
                key add NAME --git --username=username
                    adds a named github key from a user with the given github
                    username.

                key set
                    adds the ~/.ssh/id_rsa.pub key with the name specified in
                    cloudmesh.profile.user.
                    It also sets the variable key to that user.


               Once the keys are uploaded to github, they can be listed
               To list these keys the following list functions are provided.

                key list --source=git  [--username=USERNAME]
                    lists all keys in git for the specified user. If the
                    name is not specified it is read from cloudmesh.yaml
                key list --source=ssh  [--dir=DIR] [--output=OUTPUT]
                    lists all keys in the directory. If the directory is not
                    specified the default will be ~/.ssh

                key list NAMES
                    lists all keys in the named virtual machines.


                List command can use the [--output=OUTPUT] option

                    list the keys loaded to cloudmesh in the given format:
                    json, yaml, table. table is default. The NAME can be
                    specified and if omitted the name cloudmesh.profile.user
                    is assumed.

                To get keys from the cloudmesh database the following commands
                are available:

                key delete NAMES
                    deletes the Named keys. This may also have an impact on groups
                key rename NAME NEW
                    renames the key from NAME to NEW in the cloudmesh database.

               Group management of keys is an important concept in cloudmesh,
               allowing multiple users to be added to virtual machines while
               managing the keys associated with them. The keys must be uploaded
               to cloudmesh database with a name so they can be used in a
               group. The --dryrun option executes the command without
               uploading the information to the clouds. If no group name is
               specified the group name default is assumed. If no cloudnamesh
               are specified, all active clouds are assumed. active clouds
               can be set in the cloudmesh.yaml file.

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

        def print_keys(keys):
            print(Printer.write(
                keys,
                sort_keys=["name"],
                order=["name", "type", "fingerprint", "comment"],
                header=["Name", "Type", "Fingerprint", "Comment"],
                output=arguments.output)
            )

        map_parameters(arguments,
                       'check_pass',
                       'cloud',
                       'dir',
                       'dryrun',
                       'filename',
                       'force',
                       'format',
                       'name',
                       'nopass',
                       'output',
                       'pub',
                       'pwd',
                       'set_path',
                       'source')

        variables = Variables()

        if arguments.list and arguments.source == "git":

            config = Config()
            username = config["cloudmesh.profile.github"]
            keys = SSHkey().get_from_git(username)

            print_keys(keys)

            return ""

        elif arguments.list and arguments.source == "ssh":
            # this is much simpler

            sshkey = SSHkey()

            print_keys([sshkey])

            return ""

        elif arguments.list and arguments.cloud:

            clouds = Parameter.expand(arguments.cloud)

            if len(clouds) == 0:
                variables = Variables()
                cloudname = variables['cloud']
                clouds = [cloudname]
            keys = []

            for cloud in clouds:
                print(f"cloud {cloud}")
                provider = Provider(name=cloud)
                keys = provider.keys()

                provider.Print(keys, output=arguments.output, kind="key")

            return ""

        elif arguments.list:

            cloud = "local"
            db = CmDatabase()
            keys = db.find(collection=f"{cloud}-key")

            print_keys(keys)

            return ""


        elif arguments.add:

            """
            key add [NAME] [--source=FILENAME] # NOT IMPLEMENTED YET
            key add [NAME] [--source=git]
            key add [NAME] [--source=ssh]
            """

            key = Key()

            if arguments["--source"] == "ssh":
                name = arguments.NAME or "ssh"
                key.add(name, "ssh")
            elif arguments["--source"] == "git":
                name = arguments.NAME or "git"
                key.add("git", "git")
            else:
                config = Config()
                name = config["cloudmesh.profile.user"]
                kind = "ssh"
                key.add(name, kind)

        elif arguments.init:

            """
            key init 
            """

            config = Config()
            username = config["cloudmesh.profile.user"]

            if username == "TBD":
                Console.error(
                    "Please set cloudmesh.profile.user in ~/.cloudmesh.yaml")
                u = os.environ["USER"].lower().replace(" ", "")
                Console.msg(
                    f"To change it you can use the command. Define a NAME such as '{u}' e.g.")
                Console.msg("")
                Console.msg(f"  cms config set cloudmesh.profile.user={u}")
                Console.msg("")
                return ""

            key = Key()

            key.add(username, "ssh")
            variables['key'] = username

        elif arguments.upload:

            """
            key upload [NAMES] [--cloud=CLOUDS] [--dryrun]
            key upload [NAMES] [VMS] [--dryrun]
            """

            names = Parameter.expand(arguments.NAMES)

            # this may have a bug if NAMES is ommitted

            #
            # Step 0. Set keyname to variable
            #

            if names is None or len(names) == 0:
                config = Config()
                username = config["cloudmesh.profile.user"]
                names = [username]

            if len(names) == 1:
                name = names[0]
                variables = Variables()
                if "key" in variables:
                    old = variables["key"]
                    if old != name:
                        Console.msg(
                            f"Changing defualt key from {old} to {name}")
                        variables["key"] = name

            #
            # Step 1. keys = find keys to upload
            #

            cloud = "local"
            db = CmDatabase()
            db_keys = db.find(collection=f"{cloud}-key")

            keys = []
            for key in db_keys:
                if key["name"] in names:
                    keys.append(key)

            if len(keys) == 0:
                Console.error(
                    f"No keys with the names {names} found in cloudmesh. \n"
                    "       Use the command 'key add' to add the key.")

            #
            # Step 2. iterate over the clouds to upload
            #

            clouds, names = Arguments.get_cloud_and_names("list",
                                                          arguments,
                                                          variables)

            for cloud in clouds:
                print(f"cloud {cloud}")
                provider = Provider(name=cloud)
                for key in db_keys:
                    name = key['name']
                    if name in names:
                        try:
                            r = provider.key_upload(key)
                            Console.ok(f"upload key '{name} successful'. ")
                        except ValueError as e:
                            Console.error(
                                f"key '{name} already exists in {cloud}.")

            return ""


        elif arguments.delete and arguments.cloud and arguments.NAMES:

            # key delete NAMES --cloud=CLOUDS [--dryrun]
            names = Parameter.expand(arguments.NAMES)
            clouds = Parameter.expand(arguments.cloud)

            for cloud in clouds:
                provider = Provider(name=cloud)
                for name in names:
                    if arguments.dryrun:
                        Console.ok(f"Dryrun: delete {name} in {cloud}")
                    else:
                        images = provider.key_delete(name)

            return ""

        elif arguments.gen:
            """
            key gen (ssh | pem) [--filename=FILENAME] [--nopass] [--set_path]
                    [--force]
            Generate an RSA key pair with pem or ssh encoding for the public
            key. The private key is always encoded as a PEM file.
            """
            config = Config()

            # Check if password will be requested
            ap = not arguments.nopass

            if not ap:
                Console.warning("Private key will NOT have a password")
                cnt = yn_choice(message="Continue, despite risk?", default="N")
                if not cnt:
                    sys.exit()

            # Discern the name of the public and private keys
            rk_path = None
            uk_path = None
            if arguments.filename:
                fp = path_expand(arguments.filename)
                fname, fext = os.path.splitext(fp)
                if fext == ".pub" or fext == ".ssh":
                    rk_path = fname
                    uk_path = fp
                elif fext == ".priv" or fext == ".pem":
                    rk_path = fp
                    uk_path = fname + ".pub"
                else:
                    rk_path = fp
                    uk_path = rk_path + ".pub"
            else:
                rk_path = path_expand("~/.ssh/id_rsa")
                uk_path = rk_path + ".pub"

            # Check if the file exist, if so confirm overwrite
            def check_exists(path):
                if os.path.exists(path):
                    Console.info(f"{path} already exists")
                    ovwr_r = yn_choice(message=f"overwrite {path}?", default="N")
                    if not ovwr_r:
                        Console.info(f"Not overwriting {path}. Quitting")
                        sys.exit()

            if not arguments.force:
                check_exists(rk_path)
                check_exists(uk_path)

            # Set the path if requested
            if arguments.set_path:
                config['cloudmesh.security.privatekey'] = rk_path
                config['cloudmesh.security.publickey'] = uk_path
                config.save()

            Console.msg(f"\nPrivate key: {rk_path}")
            Console.msg(f"Public  key: {uk_path}\n")

            # Generate the Private and Public keys
            kh = KeyHandler()
            r = kh.new_rsa_key()
            u = kh.get_pub_key(priv=r)

            # Serialize and write the private key to the path
            sr = kh.serialize_key(key = r, key_type = "PRIV", encoding = "PEM",
                                  format = "PKCS8", ask_pass = ap)

            # Force write the key (since we check file existence above)
            kh.write_key(key = sr, path = rk_path, force = True)

            # Determine the public key format and encoding
            enc = None
            forma = None
            if arguments.ssh:
                enc = "SSH"
                forma = "SSH"
            elif arguments.pem:
                enc = "PEM"
                forma = "SubjectInfo"

            # Serialize and write the public key to the path
            su = kh.serialize_key(key = u, key_type = "PUB", encoding = enc,
                                  format = forma, ask_pass = False)

            # Force write the key (since we check file existence above)
            kh.write_key(key = su, path = uk_path, force = True)

            Console.ok("Success")

        elif arguments.verify:
            """
            key verify (ssh | pem) [--filename=FILENAME] [--pub] [--check_pass]
            Verifies the encoding (pem or ssh) of the key (private or public)
            """
            # Initialize variables
            kh = KeyHandler()

            # Determine filepath
            fp = None
            if arguments.filename is None:
                config = Config()
                kp = path_expand("~/.ssh/id_rsa")
                if arguments.pub:
                    fp = kp + ".pub"
                else:
                    fp = kp
            else:
                fp = arguments.filename

            # Discern key type
            kt = enc = None
            ap = True
            if arguments.pub:
                # Load the public key, if no error occurs formatting is correct
                kt, kta, ap = "public", "PUB", False
                # Discern public key encoding
                if arguments.ssh:
                    enc, e = "OpenSSH", "SSH"
                elif arguments.pem:  # PEM encoding
                    enc = e = "PEM"
            else:
                # Load the private key to verify the format and password of the
                # key file. If no error occurs the format and pwd are correct
                kt, kta = "private", "PRIV"
                enc = e = "PEM"
                ap = False
                if arguments.check_pass:
                    ap = True

            try:
                k = kh.load_key(path=fp, key_type=kta, encoding=e, ask_pass=ap)
                m = f"Success the {kt} key {fp} has proper {enc} format"
                Console.ok(m)
            except ValueError as e:
                # The formatting was incorrect
                m = f"Failure, {kt} key {fp} does not have proper {enc} format"
                Console.error(m)
                raise e
            except TypeError as e:
                # Success, we didn't ask the user for the key password and 
                # we received an error for not entering the password, thus
                # the key is password protectd
                if not arguments.check_pass:
                    Console.ok("The key is password protected")
                else:
                    # Error Message handled in kh.load_key()
                    raise e

        elif arguments.reformat:
            """
            key reformat (ssh | pem) [--filename=FILENAME] [--format=FORMAT]
                                      [--nopass] [--pub]
            Restructures a key's format, encoding, and password
            """

            # Initialize variables
            kh = KeyHandler()

            # Determine key type
            fname, fext = os.path.splitext(arguments.filename)
            kt = "PRIV"
            if arguments.pub or fext == ".pub":
                kt = "PUB"

            # Determine new encoding
            use_pem = True
            if arguments.ssh:
                use_pem = False

            kh.reformat_key(path = arguments.filename,
                            key_type = kt,
                            use_pem = use_pem,
                            new_format = arguments.format,
                            ask_pass = not arguments.nopass)

        elif arguments.delete and arguments.NAMES:
            # key delete NAMES [--dryrun]

            names = Parameter.expand(arguments.NAMES)

            cloud = "local"
            db = CmDatabase()
            db_keys = db.find(collection=f"{cloud}-key")

            error = []
            for key in db_keys:
                name = key['name']
                if name in names:
                    if arguments.dryrun:
                        Console.ok(f"Dryrun: delete {name}")
                    else:
                        db.delete(collection="local-key",
                                  name=name)
                        Console.ok(f"delete {name}")
            return ""

        elif arguments.group:

            raise NotImplementedError

        return ""


