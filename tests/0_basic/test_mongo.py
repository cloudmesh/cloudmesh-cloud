###############################################################
# pytest -v --capture=no tests/0_basic/test_mongo.py
# pytest -v  tests/0_basic/test_mongo.py
# pytest -v --capture=no  tests/0_basic/test_mongo.py:Test_mongo.<METHIDNAME>
###############################################################

import shutil

import os
import pytest
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate

from cloudmesh.mongo.CmDatabase import CmDatabase
from pprint import pprint


@pytest.mark.incremental
class TestMongo:

    def setup_class(self):
        self.database = CmDatabase()

        self.data = {
            "cm": {
                "kind": "test",
                "cloud": "testcloud",
                "name": "hello"
            },
            "kind": "test",
            "cloud": "testcloud",
            "name": "hello",
            "type": "test"
        }

    def test_dict(self):
        assert self.data["cm"]["kind"] == "test"

    def test_update_decorator(self):
        @DatabaseUpdate()
        def test():
            return self.data

        result = test()


"""
class TestMongo:

    def setup(self):
        self.mongo = MongoDB()

    def test_01_MongoDBControler_Borg_test(self):
        HEADING(myself())

        m1 = MongoDBController()

        PRINT("m1", m1.__dict__)

        m2 = MongoDBController()
        m3 = MongoDBController()

        m3.data["TEST"] = "test"

        PRINT("m1", m1.__dict__)
        PRINT("m2", m1.__dict__)
        PRINT("m3", m3.__dict__)

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
