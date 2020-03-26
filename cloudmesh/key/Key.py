import os
from os.path import expanduser
from pprint import pprint

from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile
from cloudmesh.configuration.Config import Config
from cloudmesh.management.configuration.SSHkey import SSHkey
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate


# noinspection PyPep8Naming
class Key(object):

    def list(self):
        cloud = "local"
        db = CmDatabase()
        keys = db.find(collection=f"{cloud}-key")
        return keys

    @classmethod
    def get_from_dir(cls, directory=None, store=True):
        directory = directory or path_expand("~/.ssh")
        # find way that also works on windows, code always must work on windows
        # and Linux, if not you need to have if condition
        os.system("chmod 700 $HOME /.ssh")
        files = [file for file in os.listdir(expanduser(path_expand(directory)))
                 if file.lower().endswith(".pub")]
        d = []
        for file in files:
            print(file)
            path = directory + "/" + file
            # find way that also works on windows, code always must work on
            # windows and Linux, if not you need to have if condition

            os.system("chmod 700 $HOME /.ssh")
            with open(path) as fd:
                for pubkey in map(str.strip, fd):
                    # skip empty lines
                    if not pubkey:
                        continue
                    print(pubkey)
                    d.append(pubkey)

        return d

    @DatabaseUpdate()
    def add(self, name=None, source=None, group=None):
        """
        key add [NAME] [--source=FILENAME]
        key add [NAME] [--source=git]
        key add [NAME] [--source=ssh]
        """
        keys = None
        if source == "git":
            config = Config()
            username = config["cloudmesh.profile.github"]
            keys = SSHkey().get_from_git(username)
            for key in keys:
                key['group'] = group or ["git"]


        elif source == "ssh":
            key = SSHkey(name=name)
            key['group'] = group or ["local", "ssh"]
            keys = [key]

        else:
            # source is filename

            key = SSHkey()

            if not group:
                group = os.path.basename(source)
                if "." in group:
                    group = [group.rsplit(".", 1)[0]]

            filename = path_expand(source)

            print (group)
            print (filename)

            lines = readfile(filename).splitlines()

            pprint(lines)

            keys = []
            for line in lines:

                key = SSHkey()

                key.add(key=line, group=group, filename=source)
                key["cm"]["name"] = key["name"] = line.split(' ',2)[2]
                keys.append(key)

            pprint(keys)

            # key = SSHkey(name=name, path=path_expand(source))
            # key['group'] = group or ["local", "ssh"]
            # keys = [key]

            for key in keys:
                print (key['name'], key['fingerprint'])
        return keys

    def export(self, group=None):

        if type(group) == list:
            groups = group
        else:
            groups = Parameter.expand(group)

        cm = CmDatabase()
        cloud = "local"


        keys = cm.find(collection=f"{cloud}-key")

        found = []
        for key in keys:

            for group in groups:
                if group in key["group"]:
                    found.append(key)
        return found

    @DatabaseUpdate()
    def add_group(self, name=None, group=None):
        names=Parameter.expand(name)
        groups=Parameter.expand(group)

        cloud = "local"
        db = CmDatabase()
        keys = db.find(collection=f"{cloud}-key")
        for key in keys:
            if key["name"] in names:
                for _group in groups:
                    if _group not in key["group"]:
                        key["group"].append(_group)
        return keys


    @DatabaseUpdate()
    def group_add(self, name=None, group=None):
        return self.group_action(name=name, group=group, action="add")

    @DatabaseUpdate()
    def group_delete(self, name=None, group=None):
        return self.group_action(name=name, group=group, action="delete")

    def group_action(self, name=None, group=None, action="add"):
        names=Parameter.expand(name)
        groups=Parameter.expand(group)

        cloud = "local"
        db = CmDatabase()
        keys = db.find(collection=f"{cloud}-key")
        for key in keys:
            if key["name"] in names:
                for _group in groups:
                    if action == "add":
                        if _group not in key["group"]:
                            key["group"].append(_group)
                    elif action == "delete":
                        if _group in key["group"]:
                            key["group"].remove(_group)
        return keys

    """
    
    Due to the bug this code has been outcommented, we will use the one from
    host insead
    
    #
    # BUG: passing cloud is not needed
    # CHECK: does the command work with >>
    #
    def vm_upload(self, group=None, cloud=None, vm=None):

        # key group upload [--group=GROUPNAMES] [--cloud=CLOUDS] [ip/vm]

        groupkeys = group


        db = CmDatabase()

        db_keys = self.cm.find(collection=f"{self.cloud}-key")
        db_keygroups = self.cm.find(collection=f"{self.cloud}-keygroup")

        keygroups = []
        for groups in db_keygroups:
            if groups["name"] == groupkeys:
                for x in groups["keys"]:
                    keygroups.append(x)

        provider = Provider(name=cloud)
        keys = ""
        for key in db_keys:
            if key["name"] in keygroups:
                keys += key["public_key"]
                keys += "\n"
                command = "echo " + keys + " >> " + "$HOME/.ssh/authorized_keys"
                # print(command, "\n")
                provider.ssh(vm, command)
                
    """
