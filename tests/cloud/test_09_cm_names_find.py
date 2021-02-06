###############################################################
# pytest -v --capture=no tests/cloud/test_09_cm_names_find.py
# pytest -v  tests/cloud/test_09_cm_names_find.py
# pytest -v --capture=no tests/cloud/test_09_cm_names_find.py::Test_cm_find::test_names_regexp
###############################################################

from pprint import pprint

import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables
from cloudmesh.mongo.CmDatabase import CmDatabase

Benchmark.debug()

cm = CmDatabase()
variables = Variables()

assert variables['cloud'] is not None
cloud = variables['cloud']

if cloud is None:
    raise ValueError("cloud is not set")

if 'benchmark_print' in variables:
    benchmark_print = variables['benchmark_print']
else:
    benchmark_print = False

benchmark_print = False


@pytest.mark.incremental
class Test_cm_find:

    def test_cm_find_collection(self):
        HEADING()
        Benchmark.Start()
        entries = cm.find(collection=f"{cloud}-vm")
        Benchmark.Stop()
        if benchmark_print:
            pprint(entries)
        else:
            print(f"Number of entries [vm]", len(entries))
        assert len(entries) > 0

    def test_cm_find_loop(self):
        HEADING()
        Benchmark.Start()
        entries = []
        for kind in ['vm', "image", "flavor"]:
            data = cm.find(cloud=f"{cloud}", kind=kind)
            if len(data) > 0:
                entries.append(data)
        if benchmark_print:
            pprint(entries)
        else:
            print(f"Number of entries [{kind}", len(data))
        Benchmark.Stop()

        assert len(entries) > 0

    def test_cm_loop(self):
        HEADING()
        names = []
        for kind in ['vm', "image", "flavor"]:
            data = cm.names(cloud=cloud, kind=kind)
            if len(data) > 0:
                names.append(data)
        if benchmark_print:
            pprint(names)
        else:
            print(f"Number of entries [{kind}]", len(data))
        assert len(names) > 0

    def test_cm_image_name_cloud(self):
        HEADING()
        Benchmark.Start()
        names = cm.names(cloud=cloud, kind="image")
        Benchmark.Stop()
        kind = "image"
        if benchmark_print:
            pprint(names)
        else:
            print(f"Number of entries [{kind}", len(names))
        assert len(names) > 0

    def test_cm_image_name_collection(self):
        HEADING()
        Benchmark.Start()
        names = cm.names(collection=f"{cloud}-image")
        Benchmark.Stop()
        kind = "image"
        if benchmark_print:
            pprint(names)
        else:
            print(f"Number of entries [{kind}", len(names))

    def test_names_regexp(self):
        HEADING()

        if cloud == 'google':
            image = "ubuntu"
        else:
            image = "Ubuntu"

        Benchmark.Start()

        names = cm.names(collection=f"{cloud}-image", regex="^CC-")

        for entry in names:
            assert "CC-" in entry

        names = cm.names(collection=f"{cloud}-image", regex=f".*{image}.*")

        for entry in names:
            assert image in entry

        kind = "image"

        if benchmark_print:
            print(names)
        else:
            print(f"Number of entries [{kind}", len(names))

        Benchmark.Stop()

    def test_cm_find_vms(self):
        HEADING()
        Benchmark.Start()
        entries = cm.find(cloud=f"{cloud},azure", kind="vm")
        Benchmark.Stop()
        kind = "vm"
        if benchmark_print:
            print(entries)
        else:
            print(f"Number of entries [{kind}", len(entries))

    def test_cm_find_ubuntu_in_images(self):
        HEADING()
        print()

        if cloud == 'google':
            image_name = "ubuntu"
        elif cloud == 'azure':
            image_name = "."
            # Azure names images differently, no ubuntu
            # shows up which causes test to fail
        else:
            image_name = "Ubuntu"

        query = {"name": {'$regex': f".*{image_name}.*"}}
        print(query)

        Benchmark.Start()
        entries = cm.find(collection=f"{cloud}-image", query=query)
        Benchmark.Stop()

        kind = "image"
        if benchmark_print:
            print(entries)
            for entry in entries:
                print(entry['name'])
        else:
            print(f"Number of entries [{kind}", len(entries))

        assert len(entries) > 0
        for entry in entries:
            assert image_name in entry['name']

    def test_cm_find_cloud_name_attributes(self):
        HEADING()
        print()

        Benchmark.Start()
        entries = cm.find(collection=f"{cloud}-vm",
                          attributes=['cm.cloud', 'cm.name'])
        Benchmark.Stop()

        kind = "vm"
        if benchmark_print:
            print(entries)
        else:
            print(f"Number of entries [{kind}", len(entries))

        assert len(entries) > 0

    def test_cm_find_cloud_name_attributes(self):
        HEADING()
        print()
        Benchmark.Start()
        entries = cm.find(collection=f"{cloud}-vm",
                          attributes=['cm.cloud', 'cm.name'])
        Benchmark.Stop()

        kind = "vm"
        if benchmark_print:
            print(entries)
        else:
            print(f"Number of entries [{kind}", len(entries))

        assert len(entries) > 0

    def test_cm_find_vm_collections(self):
        HEADING()
        Benchmark.Start()
        collections = cm.collections()
        Benchmark.Stop()

        if benchmark_print:
            print(collections)
        else:
            print(f"Number of entries [collections]", len(collections))

        assert len(collections) > 0

    def test_cm_find_vm_collections_vm(self):
        HEADING()
        Benchmark.Start()
        collections = cm.collections(regex=".*-vm")
        Benchmark.Stop()
        if benchmark_print:
            print(collections)
        else:
            print(f"Number of entries [collections]", len(collections))

        assert len(collections) > 0

    def test_cm_find_vm_collection_form_parameter(self):
        HEADING()
        Benchmark.Start()
        collections = cm.collections(
            name="a-vm,b-vm",
            regex=".*-vm")
        Benchmark.Stop()

        if benchmark_print:
            print(collections)
        else:
            print(f"Number of entries [collections]", len(collections))

        assert len(collections) == 2

    def test_benchmark(self):
        HEADING()
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)
