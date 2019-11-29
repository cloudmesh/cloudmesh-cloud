# See also the methods already implemented we have in cm for ssh management
# I think you reimplemented things that already exists.

# see and inspect cloudmesh.common
import os
from os.path import expanduser
# see content of path_expand it does expanduser as far as I know
from cloudmesh.common.util import path_expand
from cloudmesh.management.configuration.SSHkey import SSHkey
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
from cloudmesh.common.debug import VERBOSE
from pprint import pprint
from cloudmesh.configuration.Config import Config


# noinspection PyPep8Naming
class Key(object):

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
    def add(self, name, source):
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

        elif source == "ssh":
            key = SSHkey(name=name)
            keys = [key]

        else:
            raise NotImplementedError
            # source is filename

        return keys


if __name__ == "__main__":
    Key.get_from_dir(None, True)
