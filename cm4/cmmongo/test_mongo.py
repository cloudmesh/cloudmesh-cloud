from cm4.cmmongo.mongoDB import MongoDB
from cm4.configuration.config import Config


class TestMongo:

    def setup(self):
        self.status_id = "test-id-1"
        config = Config()
        self.mongo = MongoDB(host=config.get("data.mongo.MONGO_HOST"),
                             username=config.get("data.mongo.MONGO_USERNAME"),
                             password=config.get("data.mongo.MONGO_PASSWORD"),
                             port=config.get("data.mongo.MONGO_PORT"))

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
