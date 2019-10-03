###############################################################
# pytest -v --capture=no tests/test_cm_names_find.py
# pytest -v  tests/test_cm_names_find.py
###############################################################

from pprint import pprint

import pytest
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.common3.Benchmark import Benchmark

Benchmark.debug()

cm = CmDatabase()
variables = Variables()

assert variables['cloud'] is not None
cloud = variables['cloud']


@pytest.mark.incremental
class Test_cm_find:

    def test_cm_find_collection(self):
        HEADING()
        Benchmark.Start()
        entries = cm.find(collection=f"{cloud}-vm")
        Benchmark.Stop()
        print(entries)
        assert len(entries) > 0

    def test_cm_find_loop(self):
        HEADING()
        Benchmark.Start()
        entries = []
        for kind in ['vm', "image", "flavor"]:
            data = cm.find(cloud=f"{cloud}", kind=kind)
            if len(data) > 0:
                entries.append(data)
        Benchmark.Stop()
        # pprint(entries)
        assert len(entries) > 0

    def test_cm_loop(self):
        HEADING()
        names=[]
        for kind in ['vm', "image", "flavor"]:
            data = cm.names(cloud=cloud, kind=kind)
            print(names)
            if len(data) >0 :
                names.append(data)
        assert len(names) > 0

    def test_cm_image_name_cloud(self):
        HEADING()
        Benchmark.Start()
        names = cm.names(cloud=cloud, kind="image")
        Benchmark.Stop()
        # pprint(names)
        assert len(names) > 0

    def test_cm_image_name_collection(self):
        HEADING()
        Benchmark.Start()
        names = cm.names(collection=f"{cloud}-image")
        Benchmark.Stop()

        # pprint(names)

    def test_names_regexp(self):
        HEADING()
        Benchmark.Start()

        names = cm.names(collection=f"{cloud}-image", regex="^CC-")
        print(cloud, names)
        for entry in names:
            print(entry)
            assert "CC-" in entry

        names = cm.names(collection=f"{cloud}-image", regex=".*Ubuntu.*")
        pprint(names)
        for entry in names:
            print(entry)
            assert "Ubuntu" in entry
        Benchmark.Stop()


    def test_cm_find_vms(self):
        HEADING()
        Benchmark.Start()
        entries = cm.find(cloud=f"{cloud},azure", kind="vm")
        Benchmark.Stop()

        pprint(entries)

    def test_cm_find_ubuntu_in_images(self):
        HEADING()
        print()
        query = {"name": {'$regex': ".*Ubuntu.*"}}
        print(query)

        Benchmark.Start()
        entries = cm.find(collection=f"{cloud}-image", query=query)
        Benchmark.Stop()

        print(entries)
        assert len(entries) > 0

        for entry in entries:
            print(entry['name'])
            assert "Ubuntu" in entry['name']

    def test_cm_find_cloud_name_attributes(self):
        HEADING()
        print()

        Benchmark.Start()
        entries = cm.find(collection=f"{cloud}-vm",
                          attributes=['cm.cloud', 'cm.name'])
        Benchmark.Stop()

        print(entries)
        assert len(entries) > 0

    def test_cm_find_cloud_name_attributes(self):
        HEADING()
        print()
        Benchmark.Start()
        entries = cm.find(collection=f"{cloud}-vm",
                          attributes=['cm.cloud', 'cm.name'])
        Benchmark.Stop()

        print(entries)
        assert len(entries) > 0

    def test_cm_find_vm_collections(self):
        HEADING()
        Benchmark.Start()
        collections = cm.collections()
        Benchmark.Stop()

        print(collections)
        assert len(collections) > 0

    def test_cm_find_vm_collections_vm(self):
        HEADING()
        Benchmark.Start()
        collections = cm.collections(regex=".*-vm")
        Benchmark.Stop()
        print(collections)
        assert len(collections) > 0

    def test_cm_find_vm_collection_form_parameter(self):
        HEADING()
        Benchmark.Start()
        collections = cm.collections(
            name="a-vm,b-vm",
            regex=".*-vm")
        Benchmark.Stop()

        print(collections)
        assert len(collections) == 2

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)
