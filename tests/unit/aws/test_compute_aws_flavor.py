import pytest
import requests

from cloudmesh.compute.aws.AwsFlavor import AwsFlavor

@pytest.mark.incremental
class TestAWSFlavor:

    # def setup(self):
    #     self.p = Provider(name=CLOUD)

    @staticmethod
    def mock_get(url):
        print(url)
        if url == 'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json':
            return MockOfferIndexResponse()
        if url == 'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/region_index.json':
            return MockRegionIndexResponse()
        if url == 'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/20190916220712/us-east-1/index.json':
            return MockOfferFileResponse()
        else:
            RaiseException("No valid URL followed.")

    def test_flavor(self, monkeypatch):

        # apply the monkeypatch for requests.get to mock_get
        monkeypatch.setattr(requests, "get", self.mock_get)
        result = AwsFlavor.fetch_offer_file()
        # the resulting json object should be the offer file json, having gathered the path, starting offer index.
        assert result == MockOfferFileResponse.json()

        # first_result = self.p.flavor("DBCQPZ6Z853WRE98.JRTCKXETXF.6YS6EN2CT7")
        # second_result = self.p.flavor("QUMEF4UK3NPT4MN3.JRTCKXETXF.6YS6EN2CT7")

        # assert first_result['name'] == "DBCQPZ6Z853WRE98.JRTCKXETXF.6YS6EN2CT7"
        # assert first_result['vcpu'] == 48
        # assert first_result['memory'] == "384 GiB"
        # assert first_result['storage'] == "2 x 900 NVMe SSD"
        # assert first_result['clock_speed'] == "TKTK"
        # assert first_result['instance_type'] == "r5d.12xlarge"
        # assert first_result['price'] == 3.586
        # assert first_result['os'] == "RHEL"

        # assert second_result['name'] == "QUMEF4UK3NPT4MN3.JRTCKXETXF.6YS6EN2CT7"
        # assert second_result['vcpu'] == 4
        # assert second_result['memory'] == "7.5 GiB"
        # assert second_result['storage'] == "2 x 40 SSD"
        # assert second_result['clock_speed'] == "2.8 GHz"
        # assert second_result['instance_type'] == "c3.xlarge"
        # assert second_result['price'] == 0.376
        # assert second_result['os'] == "Windows"

class MockOfferIndexResponse:
    # mock json() method always returns a specific testing dictionary
    # This is a limited subset from an actual Amazon JSON offer.
    @staticmethod
    def json():
        return {
            "formatVersion" : "v1.0",
            "disclaimer" : "This pricing list is for informational purposes only. All prices are subject to the additional terms included in the pricing pages on http://aws.amazon.com. All Free Tier prices are also subject to the terms included at https://aws.amazon.com/free/",
            "publicationDate" : "2019-09-16T22:07:12Z",
            "offers" : {
                "AmazonEC2" : {
                    "offerCode" : "AmazonEC2",
                    "versionIndexUrl" : "/offers/v1.0/aws/AmazonEC2/index.json",
                    "currentVersionUrl" : "/offers/v1.0/aws/AmazonEC2/current/index.json",
                    "currentRegionIndexUrl" : "/offers/v1.0/aws/AmazonEC2/current/region_index.json"
                }
            }
        }

class MockRegionIndexResponse:
    # mock json() method always returns a specific testing dictionary
    # This is a limited subset from an actual Amazon JSON offer.
    @staticmethod
    def json():
        return {
            "formatVersion" : "v1.0",
            "disclaimer" : "This pricing list is for informational purposes only. All prices are subject to the additional terms included in the pricing pages on http://aws.amazon.com. All Free Tier prices are also subject to the terms included at https://aws.amazon.com/free/",
            "publicationDate" : "2019-09-16T22:07:12Z",
            "regions" : {
                "us-east-1" : {
                    "regionCode" : "us-east-1",
                    "currentVersionUrl" : "/offers/v1.0/aws/AmazonEC2/20190916220712/us-east-1/index.json"
                }
            }
        }

class MockOfferFileResponse:
    # mock json() method always returns a specific testing dictionary
    # This is a limited subset from an actual Amazon JSON offer.
    # As well as some fully synthetic data to ensure proper parsing
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
