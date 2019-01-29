from os.path import isfile
from cloudmesh.data.api.data import Data


class TestDataAzure:
    """
    Functional tests for the local data storage service
    """

    def setup(self):
        self.test_file_name = "1MB.dat"
        self._data = Data()
        self._data.config()

    def test_azure_01_add(self):
        cloud_file = self._data.add("azure", f"cm4/test/data/files/{self.test_file_name}")
        assert len(cloud_file.url) > 0

    def test_azure_02_ls(self):
        files = self._data.ls()
        assert len(files) > 0

    def test_azure_03_get(self):
        self._data.get(self.test_file_name, "cm4/test/data/download/")
        dl_ok = isfile(f"cm4/test/data/download/{self.test_file_name}")
        assert dl_ok is True

    def test_azure_04_del(self):
        self._data.delete(self.test_file_name)
        deleted = not self._data._providers['azure'].exists(self.test_file_name)
        assert deleted is True
