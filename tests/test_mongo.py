from cm4.mongo.mongoDB import MongoDB
from cm4.mongo.DbUpdateDecorator import SaveTo
from cm4.common.debug import HEADING, myself

# nosetest -v --nopature
# nosetests -v --nocapture tests/test_mongo.py


@SaveTo("test")
def r_dict():
    return {"name": "test-dict-1", "num": 123}


@SaveTo("test")
def r_list():
    return [
        {"name": "test-dict-1", "num": 432},
    ]


class TestMongo:

    def setup(self):
        self.mongo = MongoDB()

    def test_01_saveto(self):
        HEADING(myself())
        d = r_dict()
        assert isinstance(d, dict)
        lst = r_list()
        assert isinstance(lst, list)

    def test_02_find(self):
        HEADING(myself())
        doc = self.mongo.find_document("test", "name", "test-dict-1")
        assert doc is not None

    def test_03_delete(self):
        HEADING(myself())
        old_doc = self.mongo.delete_document("test", "name", "test-dict-1")
        assert old_doc is not None

        deleted_doc = self.mongo.find_document("test", "name", "test-dict-1")
        assert deleted_doc is None
