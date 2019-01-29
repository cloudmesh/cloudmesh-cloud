from os.path import isfile
from cloudmesh.data.api.data import Data


class TestDataLocal:
    """
    Functional tests for the local data storage service
    """

    def setup(self):
        self.test_file_name = "hello.txt"
        self._data = Data()
        self._data.config("cm4/configuration/cloudmesh.yaml")

    def test_local_01_add(self):
        self._data.add("local", f"cm4/test/data/files/{self.test_file_name}")

        storage_ref_ok = isfile(f"cm4/test/data/storage/{self.test_file_name}")
        assert storage_ref_ok is True

        # TODO: This check should be moved out of here to a db provider test.
        # Keeping for now because local is currently the only provider.
        db_ref_ok = isfile(f"cm4/test/data/db/{self.test_file_name}.yaml")
        assert db_ref_ok is True

    def test_local_02_ls(self):
        files = self._data.ls()
        assert len(files) > 0

    def test_local_03_get(self):
        self._data.get(self.test_file_name, "cm4/test/data/download/")
        dl_ok = isfile(f"cm4/test/data/download/{self.test_file_name}")
        assert dl_ok is True

    def test_local_04_del(self):
        self._data.delete(self.test_file_name)
        deleted = not self._data._providers['local'].exists(self.test_file_name)
        assert deleted is True
