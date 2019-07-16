###############################################################
# pytest -v --capture=no tests/test_cm_names_find.py
# pytest -v  tests/test_cm_names_find.py
###############################################################

import pytest
from cloudmesh.common.util import HEADING

from  cloudmesh.mongo.CmDatabase import CmDatabase
from pprint import pprint
from cloudmesh.common.variables import Variables

cm = CmDatabase()
variables = Variables()

assert variables['cloud'] is not None

cloud = variables['cloud']

@pytest.mark.incremental
class Test_cm_find:

    def test_cm_find_collection(self):
        HEADING()
        entries = cm.find (collection=f"{cloud}-vm")
        print (entries)
        assert  len(entries) > 0

    def test_cm_find_loop(self):
        HEADING()
        for kind in ['vm', "image", "flavor"]:
            entries = cm.find(cloud=f"{cloud}", kind=kind)
        pprint(entries)
        assert len(entries) > 0

    def test_cm_loop(self):
        HEADING()
        for kind in ['vm', "image", "flavor"]:
            names = cm.names(cloud=cloud, kind=kind)
            print (names)
            assert  len(names) > 0

    def test_cm_image_name_cloud(self):
        HEADING()
        names = cm.names(cloud=cloud, kind="image")
        pprint (names)
        assert len(names) > 0

    def test_cm_image_name_collection(self):
        HEADING()
        names = cm.names(collection=f"{cloud}-image")
        pprint(names)

    def test_names_regexp(self):
        HEADING()
        names = cm.names(collection=f"{cloud}-image", regex="^CC-")
        print(cloud, names)
        for entry in names:
            print(entry)
            assert "CC-" in entry

        names = cm.names(collection=f"{cloud}-image", regex=".*Ubuntu.*")
        pprint(names)
        for entry in names:
            print (entry)
            assert "Ubuntu" in entry

    def test_cm_find_vms(self):
        HEADING()
        entries = cm.find(cloud=f"{cloud},azure", kind="vm")
        pprint(entries)


    def test_cm_find_ubuntu_in_images(self):
        HEADING()
        print()
        query = {"name": {'$regex': ".*Ubuntu.*"}}
        print (query)

        entries = cm.find(collection=f"{cloud}-image", query=query)
        print (entries)
        assert len(entries) > 0

        for entry in entries:
            print (entry['name'])
            assert "Ubuntu" in entry['name']

    def test_cm_find_cloud_name_attributes(self):
        HEADING()
        print()

        entries = cm.find(collection=f"{cloud}-vm",
                          attributes=['cm.cloud', 'cm.name'])
        print (entries)
        assert len(entries) > 0

