from cloudmesh.mongo import MongoDB
from cloudmesh.mongo import MongoDBController

from cloudmesh.mongo import DatabaseUpdate
from cloudmesh.management.debug import HEADING, myself
from pprint import pprint

# nosetest -v --nopature
# nosetests -v --nocapture tests/test_mongo.py


@DatabaseUpdate("test")
def r_dict():
    return {"name": "test-dict-1", "num": 123}


@DatabaseUpdate("test")
def r_list():
    return [
        {"name": "test-dict-1", "num": 432},
    ]

def PRINT(name, d):
    print (79* "-")
    print (name)
    print (79* "-")
    pprint (d)

class TestMongo:

    def setup(self):
        self.mongo = MongoDB()

    def test_01_MongoDBControler_Borg_test(self):
        HEADING(myself())

        m1 = MongoDBController()

        PRINT ("m1", m1.__dict__)

        m2 = MongoDBController()
        m3 = MongoDBController()

        m3.data["TEST"] = "test"

        PRINT ("m1", m1.__dict__)
        PRINT ("m2", m1.__dict__)
        PRINT ("m3", m3.__dict__)

        assert m3.data["TEST"] == "test"
        assert m2.data["TEST"] == "test"
        assert m1.data["TEST"] == "test"

"""
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
"""