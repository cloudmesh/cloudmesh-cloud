###############################################################
# pytest -v --capture=no tests/aws/test_compute_aws.py
# pytest -v  tests/aws/test_compute_aws.py
# pytest -v --capture=no  tests/aws/test_compute_awas.py:Test_compute_aws.<METHIDNAME>
###############################################################
import subprocess
import time
from pprint import pprint

import pytest
from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.compute.libcloud.Provider import Provider
from cloudmesh.management.configuration.SSHkey import SSHkey
from cloudmesh.configuration.Config import Config
from cloudmesh.management.configuration.name import Name
from cloudmesh.common3.Benchmark import Benchmark

Benchmark.debug()

CLOUD= "aws"

@pytest.mark.incremental
class TestName:

    def setup(self):
        banner("setup", c="-")
        self.user = Config()["cloudmesh.profile.user"]
        self.clouduser = 'cc'
        self.name_generator = Name(
            schema=f"{self.user}-vm",
            counter=1)

        self.name = str(self.name_generator)
        self.name_generator.incr()

        self.new_name = str(self.name_generator)

        self.p = Provider(name=CLOUD)

        self.secgroupname = "CM4TestSecGroup"
        self.secgrouprule = {"ip_protocol": "tcp",
                             "from_port": 8080,
                             "to_port": 8088,
                             "ip_range": "129.79.0.0/16"}
        self.testnode = None

    def test_list_keys(self):
        HEADING()
        pprint(self.p.user)
        pprint(self.p.cloudtype)
        pprint(self.p.spec)

    def test_list_keys(self):
        HEADING()
        self.keys = self.p.keys()
        # pprint(self.keys)

        print(Printer.flatwrite(self.keys,
                                sort_keys=["name"],
                                order=["name", "fingerprint"],
                                header=["Name", "Fingerprint"])
              )

    def test_key_upload(self):
        HEADING()

        key = SSHkey()
        print(key.__dict__)

        self.p.key_upload(key)

        self.test_01_list_keys()

    def test_list_flavors(self):
        HEADING()
        flavors = self.p.flavors()
        pprint(flavors)

        print(Printer.flatwrite(flavors,
                                sort_keys=[
                                    "name", "extra.vcpu", "extra.memory",
                                    "price"],
                                order=["name", "extra.vcpu", "extra.memory",
                                       "extra.clockSpeed", "price"],
                                header=["Name", "VCPUS", "RAM", "Speed",
                                        "Price"])
              )

        """
            {'bandwidth': None,
             'cloud': 'aws',
             'created': '2019-02-22 19:27:54.965053',
             'disk': 0,
             'driver': 'aws',
             'extra': {'clockSpeed': 'Up to 3.0 GHz',
                       'currentGeneration': 'Yes',
                       'ecu': 'Variable',
                       'instanceFamily': 'General purpose',
                       'instanceType': 't2.xlarge',
                       'memory': '16 GiB',
                       'networkPerformance': 'Moderate',
                       'normalizationSizeFactor': '8',
                       'physicalProcessor': 'Intel Xeon Family',
                       'processorArchitecture': '64-bit',
                       'processorFeatures': 'Intel AVX; Intel Turbo',
                       'servicecode': 'AmazonEC2',
                       'servicename': 'Amazon Elastic Compute Cloud',
                       'storage': 'EBS only',
                       'vcpu': '4'},
             'id': 't2.xlarge',
             'kind': 'flavor',
             'name': 't2.xlarge',
             'price': 0.188,
             'ram': 16384,
             'updated': '2019-02-22 19:27:54.965053'},
        """

    def test_list_vm(self):
        HEADING()
        vms = self.p.list()
        pprint(vms)

        print(Printer.flatwrite(vms,
                                sort_keys=["name"],
                                order=["name",
                                       "state",
                                       "extra.task_state",
                                       "extra.vm_state",
                                       "extra.userId",
                                       "extra.key_name",
                                       "private_ips",
                                       "public_ips"],
                                header=["Name",
                                        "State",
                                        "Task state",
                                        "VM state",
                                        "User Id",
                                        "SSHKey",
                                        "Private ips",
                                        "Public ips"])
              )

    def test_list_secgroups(self):
        HEADING()
        secgroups = self.p.list_secgroups()
        for secgroup in secgroups:
            print(secgroup["name"])
            rules = self.p.list_secgroup_rules(secgroup["name"])

            print(Printer.write(rules,
                                sort_keys=["ip_protocol", "from_port",
                                           "to_port", "ip_range"],
                                order=["ip_protocol", "from_port", "to_port",
                                       "ip_range"],
                                header=["ip_protocol", "from_port", "to_port",
                                        "ip_range"])
                  )

    def test_secgroups_add(self):
        self.p.add_secgroup(self.secgroupname)
        self.test_05_list_secgroups()

    def test_secgroup_rules_add(self):
        rules = [self.secgrouprule]
        self.p.add_rules_to_secgroup(self.secgroupname, rules)
        self.test_05_list_secgroups()

    def test_secgroup_rules_remove(self):
        rules = [self.secgrouprule]
        self.p.remove_rules_from_secgroup(self.secgroupname, rules)
        self.test_05_list_secgroups()

    def test_secgroups_remove(self):
        self.p.remove_secgroup(self.secgroupname)
        self.test_05_list_secgroups()

    def test_create(self):
        HEADING()
        image = "CC-Ubuntu16.04"
        size = "m1.medium"
        self.p.create(name=self.name,
                      image=image,
                      size=size,
                      # username as the keypair name based on
                      # the key implementation logic
                      ex_keyname=self.user,
                      ex_security_groups=['default'])
        time.sleep(5)
        nodes = self.p.list()
        node = self.p.find(nodes, name=self.name)
        pprint(node)

        nodes = self.p.list(raw=True)
        for node in nodes:
            if node.name == self.name:
                self.testnode = node
                break

        assert node is not None

    def test_publicip_attach(self):
        HEADING()
        pubip = self.p.get_public_ip()
        pprint(pubip)
        nodes = self.p.list(raw=True)
        for node in nodes:
            if node.name == self.name:
                self.testnode = node
                break
        if self.testnode:
            print("attaching public IP...")
            self.p.attach_publicIP(self.testnode, pubip)
            time.sleep(5)
        self.test_04_list_vm()

    def test_publicip_detach(self):
        print("detaching and removing public IP...")
        time.sleep(5)
        nodes = self.p.list(raw=True)
        for node in nodes:
            if node.name == self.name:
                self.testnode = node
                break
        ipaddr = self.testnode.public_ips[0]
        pubip = self.p.cloudman.ex_get_floating_ip(ipaddr)
        self.p.detach_publicIP(self.testnode, pubip)
        time.sleep(5)
        self.test_04_list_vm()

    # def test_11_printer(self):
    #    HEADING()
    #    nodes = self.p.list()

    #    print(Printer.write(nodes, order=["name", "image", "size"]))

    # def test_01_start(self):
    #    HEADING()
    #    self.p.start(name=self.name)

    # def test_12_list_vm(self):
    #    self.test_04_list_vm()

    def test_info(self):
        HEADING()
        self.p.info(name=self.name)

    def test_destroy(self):
        HEADING()
        self.p.destroy(names=self.name)
        nodes = self.p.list()
        node = self.p.find(nodes, name=self.name)

        pprint(node)

        assert node["extra"]["task_state"] == "deleting"

    def test_list_vm(self):
        self.test_04_list_vm()

    def test_vm_login(self):
        self.test_04_list_vm()
        self.test_10_create()
        # use the self.testnode for this test
        time.sleep(30)
        self.test_11_publicIP_attach()
        time.sleep(5)
        nodes = self.p.list(raw=True)
        for node in nodes:
            if node.name == self.name:
                self.testnode = node
                break
        # pprint (self.testnode)
        # pprint (self.testnode.public_ips)
        pubip = self.testnode.public_ips[0]

        COMMAND = "cat /etc/*release*"

        ssh = subprocess.Popen(
            ["ssh", "%s@%s" % (self.clouduser, pubip), COMMAND],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        result = ssh.stdout.readlines()
        if result == []:
            error = ssh.stderr.readlines()
            print("ERROR: %s" % error)
        else:
            print("RESULT:")
            for line in result:
                line = line.decode("utf-8")
                print(line.strip("\n"))

        self.test_14_destroy()
        self.test_04_list_vm()


class takestoolong:

    def test_list_images(self):
        HEADING()
        images = self.p.images()
        pprint(images[:10])

        print(Printer.flatwrite(images[:10],
                                sort_keys=["id", "name"],
                                order=["name", "id", 'architecture',
                                       'hypervisor'],
                                header=["Name", "id", 'architecture',
                                        'hypervisor'])
              )

        """
         {'cloud': 'aws',
          'driver': 'aws',
          'extra': {'architecture': 'x86_64',
                    'billing_products': [],
                    'block_device_mapping': [{'device_name': '/dev/sda1',
                                              'ebs': {'delete': 'true',
                                                      'iops': None,
                                                      'snapshot_id': 'snap-0286f41a178e9566b',
                                                      'volume_id': None,
                                                      'volume_size': 8,
                                                      'volume_type': 'gp2'},
                                              'virtual_name': None}],
                    'description': None,
                    'ena_support': None,
                    'hypervisor': 'xen',
                    'image_location': 'amazon/aws-elasticbeanstalk-amzn-2017.09.1.x86_64-golang-pv-201801050757',
                    'image_type': 'machine',
                    'is_public': 'true',
                    'kernel_id': 'aki-5c21674b',
                    'owner_alias': 'amazon',
                    'owner_id': '102837901569',
                    'platform': None,
                    'ramdisk_id': None,
                    'root_device_type': 'ebs',
                    'sriov_net_support': None,
                    'state': 'available',
                    'tags': {},
                    'virtualization_type': 'paravirtual'},
          'id': 'ami-3b560641',
          'kind': 'image',
          'name': 'aws-elasticbeanstalk-amzn-2017.09.1.x86_64-golang-pv-201801050757'},
        """

    def test_flavor(self, monkeypatch):
        def mock_get(*args, **kwargs):
            return MockOfferResponse()

        # apply the monkeypatch for requests.get to mock_get
        monkeypatch.setattr(requests, "get", mock_get)
        self.p.flavors()
        first_result = self.p.flavor("DBCQPZ6Z853WRE98.JRTCKXETXF.6YS6EN2CT7")
        second_result = self.p.flavor("QUMEF4UK3NPT4MN3.JRTCKXETXF.6YS6EN2CT7")

        assert first_result['name'] == "DBCQPZ6Z853WRE98.JRTCKXETXF.6YS6EN2CT7"
        assert first_result['vcpu'] == 48
        assert first_result['memory'] == "384 GiB"
        assert first_result['storage'] == "2 x 900 NVMe SSD",
        assert first_result['clock_speed'] == "TKTK"
        assert first_result['instance_type'] == "r5d.12xlarge"
        assert first_result['price'] == 3.586
        assert first_result['os'] == "RHEL"

        assert second_result['name'] == "QUMEF4UK3NPT4MN3.JRTCKXETXF.6YS6EN2CT7"
        assert second_result['vcpu'] == 4
        assert second_result['memory'] == "7.5 GiB"
        assert second_result['storage'] == "2 x 40 SSD",
        assert second_result['clock_speed'] == "2.8 GHz"
        assert second_result['instance_type'] == "c3.xlarge"
        assert second_result['price'] == 0.376
        assert second_result['os'] == "Windows"

class MockOfferResponse:

    # mock json() method always returns a specific testing dictionary
    # This is a limited subset from an actual Amazon JSON offer.
    @staticmethod
    def json():
        return {
            "formatVersion" : "v1.0",
            "disclaimer" : "This pricing list is for informational purposes only. All prices are subject to the additional terms included in the pricing pages on http://aws.amazon.com. All Free Tier prices are also subject to the terms included at https://aws.amazon.com/free/",
            "offerCode" : "AmazonEC2",
            "version" : "20190916220712",
            "publicationDate" : "2019-09-16T22:07:12Z",
            "products" : {
                "DBCQPZ6Z853WRE98" : {
                    "sku" : "DBCQPZ6Z853WRE98",
                    "productFamily" : "Compute Instance",
                    "attributes" : {
                        "servicecode" : "AmazonEC2",
                        "location" : "US East (N. Virginia)",
                        "locationType" : "AWS Region",
                        "instanceType" : "r5d.12xlarge",
                        "currentGeneration" : "Yes",
                        "instanceFamily" : "Memory optimized",
                        "vcpu" : "48",
                        "physicalProcessor" : "Intel Xeon Platinum 8175",
                        "memory" : "384 GiB",
                        "storage" : "2 x 900 NVMe SSD",
                        "networkPerformance" : "10 Gigabit",
                        "processorArchitecture" : "64-bit",
                        "tenancy" : "Shared",
                        "operatingSystem" : "RHEL",
                        "licenseModel" : "No License required",
                        "usagetype" : "UnusedBox:r5d.12xlarge",
                        "operation" : "RunInstances:0010",
                        "capacitystatus" : "UnusedCapacityReservation",
                        "ecu" : "173",
                        "instancesku" : "G3MK8SR8Z65JVC4X",
                        "normalizationSizeFactor" : "96",
                        "preInstalledSw" : "NA",
                        "servicename" : "Amazon Elastic Compute Cloud"
                    }
                },
                "QUMEF4UK3NPT4MN3" : {
                    "sku" : "QUMEF4UK3NPT4MN3",
                    "productFamily" : "Compute Instance",
                    "attributes" : {
                        "servicecode" : "AmazonEC2",
                        "location" : "US East (N. Virginia)",
                        "locationType" : "AWS Region",
                        "instanceType" : "c3.xlarge",
                        "currentGeneration" : "No",
                        "instanceFamily" : "Compute optimized",
                        "vcpu" : "4",
                        "physicalProcessor" : "Intel Xeon E5-2680 v2 (Ivy Bridge)",
                        "clockSpeed" : "2.8 GHz",
                        "memory" : "7.5 GiB",
                        "storage" : "2 x 40 SSD",
                        "networkPerformance" : "Moderate",
                        "processorArchitecture" : "64-bit",
                        "tenancy" : "Shared",
                        "operatingSystem" : "Windows",
                        "licenseModel" : "No License required",
                        "usagetype" : "UnusedBox:c3.xlarge",
                        "operation" : "RunInstances:0002",
                        "capacitystatus" : "UnusedCapacityReservation",
                        "ecu" : "14",
                        "enhancedNetworkingSupported" : "Yes",
                        "instancesku" : "7MS6E9W2YWKJZRX5",
                        "normalizationSizeFactor" : "8",
                        "preInstalledSw" : "NA",
                        "processorFeatures" : "Intel AVX; Intel Turbo",
                        "servicename" : "Amazon Elastic Compute Cloud"
                    }
                },
            },
            "terms" : {
                "OnDemand" : {
                    "DBCQPZ6Z853WRE98" : {
                        "DBCQPZ6Z853WRE98.JRTCKXETXF" : {
                            "offerTermCode" : "JRTCKXETXF",
                            "sku" : "DBCQPZ6Z853WRE98",
                            "effectiveDate" : "2019-09-01T00:00:00Z",
                            "priceDimensions" : {
                                "DBCQPZ6Z853WRE98.JRTCKXETXF.6YS6EN2CT7" : {
                                    "rateCode" : "DBCQPZ6Z853WRE98.JRTCKXETXF.6YS6EN2CT7",
                                    "description" : "$3.586 per Unused Reservation RHEL r5d.12xlarge Instance Hour",
                                    "beginRange" : "0",
                                    "endRange" : "Inf",
                                    "unit" : "Hrs",
                                    "pricePerUnit" : {
                                        "USD" : "3.5860000000"
                                    },
                                    "appliesTo" : [ ]
                                }
                            },
                            "termAttributes" : { }
                        }
                    },
                    "QUMEF4UK3NPT4MN3" : {
                        "QUMEF4UK3NPT4MN3.JRTCKXETXF" : {
                            "offerTermCode" : "JRTCKXETXF",
                            "sku" : "QUMEF4UK3NPT4MN3",
                            "effectiveDate" : "2019-09-01T00:00:00Z",
                            "priceDimensions" : {
                                "QUMEF4UK3NPT4MN3.JRTCKXETXF.6YS6EN2CT7" : {
                                    "rateCode" : "QUMEF4UK3NPT4MN3.JRTCKXETXF.6YS6EN2CT7",
                                    "description" : "$0.376 per Unused Reservation Windows c3.xlarge Instance Hour",
                                    "beginRange" : "0",
                                    "endRange" : "Inf",
                                    "unit" : "Hrs",
                                    "pricePerUnit" : {
                                        "USD" : "0.3760000000"
                                    },
                                    "appliesTo" : [ ]
                                }
                            },
                            "termAttributes" : { }
                        }
                    },
                },
            }
}

class other:

    def test_rename(self):
        HEADING()

        self.p.rename(source=self.name, destination=self.new_name)

    # def test_01_stop(self):
    #    HEADING()
    #    self.stop(name=self.name)

    # def test_01_suspend(self):
    #    HEADING()
    #    self.p.suspend(name=self.name)

    # def test_01_resume(self):
    #    HEADING()
    #    self.p.resume(name=self.name)
