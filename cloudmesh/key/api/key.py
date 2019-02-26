import os
from os.path import expanduser
from cloudmesh.common.util import path_expand


# noinspection PyPep8Naming
class Key(object):

    @classmethod
    def get_from_dir(cls, directory=None, store=True):
        directory = directory or path_expand("~/.ssh")
        os.system("chmod 700 $HOME /.ssh")
        files = [file for file in os.listdir(expanduser(path_expand(directory)))
                 if file.lower().endswith(".pub")]
        d = []
        for file in files:
            print(file)
            path = directory + "/" + file
            os.system("chmod 700 $HOME /.ssh")
            with open(path) as fd:
                for pubkey in map(str.strip, fd):
                    # skip empty lines
                    if not pubkey:
                        continue
                    print(pubkey)
                    d.append(pubkey)

        return d



if __name__ == "__main__":
    Key.get_from_dir(None, True)
