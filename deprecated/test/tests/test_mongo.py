from cloudmesh.mongo import MongoDB
from cloudmesh.management.configuration.config import Config


#
# TODO: convert to a nosetest
#

class TestMongo:

    def __init__(self):
        self.status_id = None
        self.mongo = None

    def setup(self):
        self.status_id = "test-id-1"
        config = Config().data["cloudmesh"]["data"]["mongo"]
        self.mongo = MongoDB(host=config["MONGO_HOST"],
                             username=config["MONGO_USERNAME"],
                             password=config["MONGO_PASSWORD"],
                             port=config["MONGO_PORT"])

    def test_01_insert_status(self):
        status = self.mongo.status_document(self.status_id, "running", "job-id-1", "history")
        post_id = self.mongo.insert_status_collection(status)
        assert post_id is not None

    def test_02_find(self):
        doc = self.mongo.find_document("status", "id", self.status_id)
        assert doc is not None

    def test_03_delete(self):
        old_doc = self.mongo.delete_document("status", "id", self.status_id)
        assert old_doc is not None

        deleted_doc = self.mongo.find_document("status", "id", self.status_id)
        assert deleted_doc is None
