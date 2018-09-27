from libcloud.storage.types import Provider
from libcloud.storage.providers import get_driver
from CloudFile import CloudFile
from storage.StorageProviderABC import StorageProviderABC


class AzureStorageProvider(StorageProviderABC):

    def __init__(self, account_name, access_key, container='cmdata'):
        '''
        Initialize Azure storage driver.
        Todo: create container if it doesn't exist.
        '''
        driver = get_driver(Provider.AZURE_BLOBS)
        self._driver = driver(key=account_name, secret=access_key)
        self._container = self._driver.get_container(container_name=container)
        self._container_url = self._container.extra.get('url').replace('http', 'https')

    def add(self, local_path):
        '''
        Upload a new file.
        
        :param local_path: Path to a file that will be stored.
        :return: a CloudFile with resource information filled in
        '''
        cloud_file = CloudFile().from_local_path(local_path)
        cloud_file.service = 'azure'
        cloud_file.url =  self._container_url + '/' + cloud_file.name
        
        # Libcloud's `upload_object_via_stream` to azure is currently broken:
        # https://issues.apache.org/jira/browse/LIBCLOUD-993
        self._driver.upload_object(file_path=local_path,
                                container=self._container,
                                object_name=cloud_file.name)

        return cloud_file

    def get(self, cloud_file, local_dest):
        '''
        Download the file from the `cloud_file.url` to a local folder.

        :param cloud_file: A cloud file entry from the db. 
        :param local_dest: A local path where the cloud file will be downloaded.
        '''

        # For some reason, if `local_dest` does not have a trailing slash,
        # a permission error is thrown. Could be Windows specific.
        if local_dest[-1] != '/' and local_dest[-1] != '\\':
            local_dest += '/'
        
        obj = self._get_object(cloud_file.name)
        self._driver.download_object(obj, local_dest, overwrite_existing=True)

    def delete(self, cloud_file):
        '''
        Delete a file from the database

        :param cloud_file: the cloud file entry being deleted
        '''
        obj = self._get_object(cloud_file.name)
        self._driver.delete_object(obj)

    def _get_object(self, obj_name):
        ''' 
        Gets and object that can be used with the storage driver's methods.
        '''
        return self._driver.get_object(self._container.name, obj_name)
