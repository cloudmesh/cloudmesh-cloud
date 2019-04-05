from os.path import isfile
from cloudmesh.data.api.data import Data


# TODO: The directories and files for the test should be created on the fly.
# for example if a 1mb data file is needed it needs to be created if it does
# not exist. It neews do be placed in a temproary directory and not in the
# code itself. There may be in pathlib special features to declare tmp files.
# if not i suggest ~/.cloudmesh/tmp

class TestDataLocal:
    """
    Functional tests for the local data storage service
    """

    def setup(self):
        self.test_file_name = "hello.txt"
        self._data = Data()
        self._data.config("cloud/configuration/cloudmesh.yaml")

        # TODO: this needs to be configured in cloudmesh4.yaml with Config()


    def test_local_01_add(self):
        self._data.add("local", f"cloud/test/data/files/{self.test_file_name}")

        storage_ref_ok = isfile(f"cloud/test/data/storage/{self.test_file_name}")
        assert storage_ref_ok is True

        # TODO: This check should be moved out of here to a db provider test.
        # Keeping for now because local is currently the only provider.
        db_ref_ok = isfile(f"cloud/test/data/db/{self.test_file_name}.yaml")
        assert db_ref_ok is True

    def test_local_02_ls(self):
        files = self._data.ls()
        assert len(files) > 0

    def test_local_03_get(self):
        self._data.get(self.test_file_name, "cloud/test/data/download/")
        dl_ok = isfile(f"cloud/test/data/download/{self.test_file_name}")
        assert dl_ok is True

    def test_local_04_del(self):
        self._data.delete(self.test_file_name)
        deleted = not self._data._providers['local'].exists(self.test_file_name)
        assert deleted is True
