"""Cloudmesh Multi Service Data Access

Usage:
  cloud data add FILE
  cloud data add SERVICE FILE
  cloud data get FILE
  cloud data get FILE DEST_FOLDER
  cloud data del FILE
  cloud data (ls | dir)
  cloud data (-h | --help)
  cloud data --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --config      Location of a cmdata.yaml file
"""

from docopt import docopt
from cloudmesh.data.api.db import LocalDBProvider
from cloudmesh.data.api.storage import LocalStorageProvider
from cloudmesh.data.api.storage import AzureStorageProvider
from cloudmesh.management.configuration.config import Config


class Data(object):

    def __init__(self):
        self._db = None
        self._conf = {}
        self._providers = {}

    def config(self, config_path='~/.cloudmesh/cloudmesh4.yaml'):
        """
        Use `cloudmesh4.yaml` file to configure.
        """
        self._conf = Config(config_path).get("data")

        # Set DB provider. There should only be one.
        db_provider = self._conf.get('default.db')

        if db_provider == 'local':
            db_path = self._conf.get('db.local.CMDATA_DB_FOLDER')
            self._db = LocalDBProvider(db_path)

        # Check for local storage provider.
        storage_path = self._conf.get('service.local.CMDATA_STORAGE_FOLDER')
        if storage_path:
            self._providers['local'] = LocalStorageProvider(storage_path)

        # Check for Azure provider.
        az_conf = self._conf.get('service.azure')
        if az_conf:
            az_act = az_conf.get('credentials.AZURE_STORAGE_ACCOUNT')
            az_key = az_conf.get('credentials.AZURE_STORAGE_KEY')
            az_container = az_conf.get('container')
            if az_act and az_key:
                self._providers['azure'] = AzureStorageProvider(az_act, az_key, az_container)

        # Set a default storage provider.
        default_storage_provider = self._conf.get('default.service')
        self._providers['default'] = self._providers[default_storage_provider]

    def ls(self):
        """
        List tracked files.

        :return: A list of CloudFiles
        """
        files = self._db.list_files()

        self._print_row("FILE", "SERVICE", "SIZE", "URL")

        for f in files:
            self._print_row(f.name, f.service, f.size, f.url)

        return files

    def add(self, provider, file_path):
        """
        Add a new file

        :param provider: The storage provider where the file should be stored.
        :param file_path: The local path to the file.
        """
        new_cloud_file = self._providers[provider or 'default'].put(file_path)
        self._db.put(new_cloud_file)
        return new_cloud_file

    def get(self, file_name, dest_folder='.'):
        """

        Retrieve a file

        :param file_name: The name corresponding to the cloud file to be downloaded.
        :param dest_folder:
        :return:
        """
        # Get db entry for this file
        cloud_file = self._db.get(file_name)

        if not cloud_file:
            print("Requested file not found. Use `ls` to see a list of file names.")
            raise SystemExit

        # Todo: docopt default for this?
        dest_folder = dest_folder or '.'
        self._providers[cloud_file.service].get(cloud_file, dest_folder)

    def delete(self, file_name):
        """
        Remove a file

        :param file_name: The name of the file to remove.
        """
        cloud_file = self._db.get(file_name)

        if cloud_file is None:
            raise Exception(f"{file_name} not found in the database.")

        self._providers[cloud_file.service].delete(cloud_file)
        self._db.delete(cloud_file)

    @staticmethod
    def _print_row(file_name, service, size, url):
        """
        Print a formatted row
        """
        print(" %-35s %-10s %-10s %-50s" % (file_name, service, size, url))


def process_arguments(args):
    cd = Data()
    cd.config()

    if args['ls'] or args['dir']:
        cd.ls()
    elif args['add'] and args['FILE']:
        cd.add(args['SERVICE'], args['FILE'])
    elif args['del'] and args['FILE']:
        cd.delete(args['FILE'])
    elif args['get'] and args['FILE']:
        cd.get(args['FILE'], args['DEST_FOLDER'])


if __name__ == "__main__":
    arguments = docopt(__doc__, version='Cloudmesh Drive')
    process_arguments(arguments)
