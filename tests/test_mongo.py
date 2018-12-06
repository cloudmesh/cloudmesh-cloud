import time
from cm4.vm.Vm import Vm
from cm4.configuration.config import Config
from cm4.mongo.mongoDB import MongoDB
from cm4.common.debug import HEADING, myself

# nosetest -v --nopature
# nosetests -v --nocapture tests/test_mongo.py


class TestMongo:

    def setup(self):
        self.status_id = "test-id-1"
        config = Config().data["cloudmesh"]["data"]["mongo"]
        self.mongo = MongoDB(host=config["MONGO_HOST"],
                             username=config["MONGO_USERNAME"],
                             password=config["MONGO_PASSWORD"],
                             port=config["MONGO_PORT"])

    def test_01_insert_status(self):
        HEADING(myself())
        status = self.mongo.status_document(self.status_id, "running", "job-id-1", "history")
        post_id = self.mongo.insert_status_collection(status)
        assert post_id is not None

    def test_02_find(self):
        HEADING(myself())
        doc = self.mongo.find_document("status", "id", self.status_id)
        assert doc is not None

    def test_03_delete(self):
        HEADING(myself())
        old_doc = self.mongo.delete_document("status", "id", self.status_id)
        assert old_doc is not None

        deleted_doc = self.mongo.find_document("status", "id", self.status_id)
        assert deleted_doc is None
