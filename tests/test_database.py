from cloudmesh.common.util import HEADING

from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.common.Printer import Printer
#from cloudmesh.mongo import MongoDBController

#from cloudmesh.mongo import DatabaseUpdate
#from cloudmesh.management.debug import HEADING, myself
from pprint import pprint

from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
from cloudmesh.management.configuration.name import Name

# nosetest -v --nopature
# nosetests -v --nocapture tests/test_database.py

class TestMongo:

    def setup(self):
        self.database = CmDatabase()
        self.database.clear()

    def test_01_status(self):
        HEADING()
        r = self.database.status()
        pprint(r)
        assert "Connection refused" not in r

        d = {}
        for field in ['uptime', 'pid', 'version', 'host']:
            d[field]=r[field]

        print (Printer.attribute(d))

        assert d is not None

    def test_02_update(self):
        HEADING()

        entries = [{"cmid" : 1, "name" : "Gregor"},
                   {"cmid" : 2, "name" : "Laszewski"}]
        self.database.update(entries)

    def test_03_update(self):
        HEADING()

        r = self.database.find(name="Gregor")

        pprint (r)

    def test_04_update(self):
        HEADING()

        entries = [{"cmid" : 1, "name" : "gregor"},
                   {"cmid" : 2, "name" : "laszewski"}]
        self.database.update(entries, replace=True)

    def test_05_update(self):
        HEADING()

        r = self.database.find(name="gregor")

        pprint (r)

    def test_06_find_by_id(self):
        HEADING()
        r = self.database.find_by_id(1)

        pprint (r)

        r = self.database.find_by_id(2)

        pprint (r)

    def test_07_decorator(self):
        HEADING()

        @DatabaseUpdate(collection="cloudmesh")
        def entry():
            return {"cmid" : 3, "name" : "albert"}


        a = entry()

        r = self.database.find_by_id(3)

        pprint (r)

    def test_08_find_by_id(self):
        HEADING()
        r = self.database.find()

        pprint (r)

        assert len(r) == 3

    def test_09_overwrite(self):
        HEADING()

        entries = [{"cmid" : 1, "name" : "gregor", "phone": "android"}]
        self.database.update(entries, replace=True)

        r = self.database.find()

        pprint (r)

        assert len(r) == 3


    def test_10_fancy(self):
        HEADING()

        counter = 1

        n = Name(experiment="exp",
                 group="grp",
                 user="gregor",
                 kind="vm",
                 counter=counter)

        print (n)

        entries = [{
              "cmcounter" : counter,
              "cmid": n,
              "name" : "gregor",
              "phone": "android"
        }]
        self.database.update(entries, replace=True)

        r = self.database.find()

        pprint (r)

        #assert len(r) == 3



"""
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