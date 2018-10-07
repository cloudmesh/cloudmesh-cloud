import getpass
import datetime
from os.path import isfile, abspath, basename, getsize


class CloudFile(object):
    yaml_tag = u"!CloudFile"

    """
    Model for cloud file database entry.
    """

    def __init__(self):
        self.name = ''
        self.owner = getpass.getuser()
        self.size = 0
        self.date_created = datetime.datetime.now()
        self.date_modified = datetime.datetime.now()
        self.date_touched = datetime.datetime.now()
        self.service = ''
        self.url = ''
        self.policies = []

    def from_local_path(self, file_path):
        file_path = abspath(file_path)

        if not isfile(file_path):
            return self

        self.name = basename(file_path)
        self.size = getsize(file_path)

        return self
