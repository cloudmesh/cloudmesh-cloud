###############################################################
# pytest -v --capture=no tests/azure/test_compute_pyazure.py
# pytest  tests/azure/test_compute_pyazure.py
###############################################################

CLOUD="azure"

import pytest
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.common3.Benchmark import Benchmark

from cloudmesh.configuration.Config import Config
from cloudmesh.management.configuration.name import Name


if CLOUD == "azure":
    from cloudmesh.compute.azure.Provider import Provider

# is this the same test as in cloud 06 ?, we need to make the test much more
# similar

Benchmark.debug()

user = Config()["cloudmesh.profile.user"]

SECGROUP=f"cloudmesh_{user}"
SECGROUP_UPLOAD=f"cloudmesh_{user}_upload"

@pytest.mark.incremental
class TestAzure:

    def setup(self):
        banner("setup", c="-")
        self.user = Config()["cloudmesh.profile.user"]
        self.name_generator = Name(
            schema=f"{self.user}-vm",
            counter=1)

        self.name = str(self.name_generator)
        self.name_generator.incr()

        self.new_name = str(self.name_generator)
        self.p = Provider(name=CLOUD)

    def test_resource_group(self):
        HEADING()
        Benchmark.Start()
        test_resource_group = self.p._get_resource_group()
        VERBOSE(test_resource_group, label='RESOURCE GROUP')
        Benchmark.Stop()

        assert test_resource_group is not None

    def test_list_images(self):
        HEADING()

        Benchmark.Start()
        test_images = self.p.images()
        Benchmark.Stop()
        VERBOSE(test_images, label='Azure List of Images')

        assert test_images is not None

    def test_list_flavors(self):
        HEADING()

        Benchmark.Start()
        test_flavors = self.p.flavors()
        Benchmark.Stop()
        VERBOSE(test_flavors, label='Azure List of Flavors')

        assert test_flavors is not None

    def test_create_vm(self):
        HEADING()

        Benchmark.Start()
        test_vm = self.p.create()
        Benchmark.Stop()
        VERBOSE(test_vm, label='Virtual Machine Created')

        assert test_vm is not None

    def test_set_server_metadata(self):
        HEADING()

        tags = 'This is my cloudmesh metadata Tag'

        Benchmark.Start()
        test_set_metadata = self.p.set_server_metadata(name=None,cm=tags)
        Benchmark.Stop()
        VERBOSE(test_set_metadata, label='Added Metadata to Virtual Machine Created')

        assert test_set_metadata is not None

    def test_get_server_metadata(self):
        HEADING()

        Benchmark.Start()
        test_get_metadata = self.p.get_server_metadata(self)
        Benchmark.Stop()
        VERBOSE(test_get_metadata, label='Get Metadata from Virtual Machine')

        assert test_get_metadata is not None

    def test_delete_server_metadata(self):
        HEADING()

        Benchmark.Start()
        test_delete_metadata = self.p.delete_server_metadata(None, 'cm')
        Benchmark.Stop()
        VERBOSE(test_delete_metadata, label='Metadata from Virtual Machine after deleting tag')

        assert test_delete_metadata is not None

    def test_list_security_groups(self):
        HEADING()

        Benchmark.Start()
        test_list_sec_groups = self.p.list_secgroups()
        Benchmark.Stop()
        VERBOSE(test_list_sec_groups, label='List Security Groups')

        assert test_list_sec_groups is not None

    def test_add_security_group(self):
        HEADING()

        Benchmark.Start()
        #
        # BUG secgroup must be named argument
        #
        test_add_sec_group = self.p.add_secgroup(SECGROUP, description=None)
        Benchmark.Stop()
        VERBOSE(test_add_sec_group, label='Add Security Group')

        assert test_add_sec_group is not None

    def test_add_security_rule(self):
        HEADING()

        Benchmark.Start()
        test_add_sec_rule = self.p.add_secgroup_rule(name='resource_name_security_rule',
                                                     port=None,protocol=None,
                                                     ip_range='3389:3390')
        Benchmark.Stop()
        VERBOSE(test_add_sec_rule, label='Add Security Rule')

        assert test_add_sec_rule is not None

    def test_list_security_group_rules(self):
        HEADING()

        Benchmark.Start()
        test_list_secgroup_rules = self.p.list_secgroup_rules(name=SECGROUP)
        Benchmark.Stop()
        VERBOSE(test_list_secgroup_rules, label='List Security Group Rules')

        assert test_list_secgroup_rules is not None

    def test_remove_security_rule(self):
        HEADING()

        Benchmark.Start()
        test_remove_sec_rule = self.p.remove_rules_from_secgroup(name=SECGROUP,
                                                                 rules='resource_name_security_rule')
        Benchmark.Stop()
        VERBOSE(test_remove_sec_rule, label='Remove Security Rule')

        assert test_remove_sec_rule is not None

    def test_remove_security_group(self):
        HEADING()

        Benchmark.Start()
        test_remove_sec_group = self.p.remove_secgroup(name=SECGROUP)
        Benchmark.Stop()
        VERBOSE(test_remove_sec_group, label='Remove Security Rule')

        assert test_remove_sec_group is None

    def test_upload_security_group(self):
        HEADING()

        # BUG: this seems wrong: cloudmesh_upload

        Benchmark.Start()
        test_upload_secgroup = self.p.upload_secgroup(name=SECGROUP_UPLOAD)
        Benchmark.Stop()
        VERBOSE(test_upload_secgroup, label='Upload Security Group')

        assert test_upload_secgroup is None

    def test_add_rules_to_security_group(self):
        HEADING()

        # BUG: this seems wrong: cloudmesh_upload

        Benchmark.Start()
        test_add_rules_to_secgroup = self.p.add_rules_to_secgroup(
            secgroupname=SECGROUP_UPLOAD,
            newrules='resource_name_security_rule_upload')
        Benchmark.Stop()
        VERBOSE(test_add_rules_to_secgroup, label='Add Rules to Security Group')

        assert test_add_rules_to_secgroup is None

    def test_start(self):
        HEADING()

        Benchmark.Start()
        start_vm = self.p.start()
        Benchmark.Stop()
        VERBOSE(start_vm, label='Starting Virtual Machine')

        assert start_vm is not None

    def test_info(self):
        HEADING()

        Benchmark.Start()
        info_vm = self.p.info(None, None)
        Benchmark.Stop()
        VERBOSE(info_vm, label='Get Virtual Machine Info')

        assert info_vm is not None

    def test_list_vms(self):
        HEADING()

        Benchmark.Start()
        list_vm = self.p.list()
        Benchmark.Stop()
        VERBOSE(list_vm, label='List Virtual Machines')

        assert list_vm is not None

    def test_reboot(self):
        HEADING()

        Benchmark.Start()
        reboot_vm = self.p.reboot()
        Benchmark.Stop()
        VERBOSE(reboot_vm, label='Rebooting Virtual Machine')

        assert reboot_vm is not None

    def test_suspend(self):
        HEADING()

        Benchmark.Start()
        suspend_vm = self.p.suspend()
        Benchmark.Stop()
        VERBOSE(suspend_vm, label='Suspend Virtual Machine')

        assert suspend_vm is not None

    def test_resume(self):
        HEADING()

        Benchmark.Start()
        resume_vm = self.p.resume()
        Benchmark.Stop()
        VERBOSE(resume_vm, label='Resume Virtual Machine')

        assert resume_vm is not None

    def test_stop(self):
        HEADING()

        Benchmark.Start()
        stop_vm = self.p.stop()
        Benchmark.Stop()
        VERBOSE(stop_vm, label='Stop Virtual Machine')

        assert stop_vm is not None

    def test_destroy(self):
        HEADING()

        Benchmark.Start()
        destroy_vm = self.p.destroy()
        Benchmark.Stop()
        VERBOSE(destroy_vm, label='Destroy Virtual Machine')

        assert destroy_vm is None

    def test_benchmark(self):
        Benchmark.print()
