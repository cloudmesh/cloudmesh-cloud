import json
import urllib.request

# please use requests

"""
I do not yet understand why flavor is restricted and we do not just use what the dict under product returns

 I see for example. Are all of them returned, or just some selected values?
 
 {
    "WR4JPHDYW77XS7MC" : {
      "sku" : "WR4JPHDYW77XS7MC",
      "productFamily" : "Compute Instance",
      "attributes" : {
        "servicecode" : "AmazonEC2",
        "location" : "South America (Sao Paulo)",
        "locationType" : "AWS Region",
        "instanceType" : "c3.8xlarge",
        "currentGeneration" : "No",
        "instanceFamily" : "Compute optimized",
        "vcpu" : "32",
        "physicalProcessor" : "Intel Xeon E5-2680 v2 (Ivy Bridge)",
        "clockSpeed" : "2.8 GHz",
        "memory" : "60 GiB",
        "storage" : "2 x 320 SSD",
        "networkPerformance" : "10 Gigabit",
        "processorArchitecture" : "64-bit",
        "tenancy" : "Dedicated",
        "operatingSystem" : "SUSE",
        "licenseModel" : "No License required",
        "usagetype" : "SAE1-UnusedDed:c3.8xlarge",
        "operation" : "RunInstances:000g",
        "capacitystatus" : "UnusedCapacityReservation",
        "ecu" : "108",
        "enhancedNetworkingSupported" : "Yes",
        "instancesku" : "FKFNCVGF8F4VBXQ4",
        "normalizationSizeFactor" : "64",
        "preInstalledSw" : "NA",
        "processorFeatures" : "Intel AVX; Intel Turbo",
        "servicename" : "Amazon Elastic Compute Cloud"
      }

"""


class AwsFlavor(object):

    def __init__(self):
        pass

    def get(self):
        output = []
        for key in self.__dict__:
            output.append(self.__dict__.get(key))
        return output

    def update(self, dict={}):
        # Note that dict is overwritten, and will be ignored
        offer_file = self.fetch_offer_file()
        dict = self.parse_offer_file(offer_file)
        self.__dict__ = dict

    @staticmethod
    def fetch_json_file(url):
        with urllib.request.urlopen(url) as req:
            data = json.loads(req.read().decode())
            return data

    def fetch_offer_file(self,
                         url=None,
                         region="us-east-1",
                         offer='AmazonEC2'
                         ):
        if url is None:
            offer_index_url = f"https://pricing.{region}.amazonaws.com/offers/v1.0/aws/index.json"
            offer_index = self.fetch_json_file(offer_index_url)
            offer_file_api_url = f"https://pricing.{region}.amazonaws.com"
            # offer_file_path = offer_index['offers']['AmazonEC2']['currentVersionUrl']
            region_file_path = offer_index['offers'][offer]['currentRegionIndexUrl']
            regions_url = offer_file_api_url + region_file_path
            regions_file = self.fetch_json_file(regions_url)
            offer_file_path = regions_file["regions"][region]["currentVersionUrl"]
            url = offer_file_api_url + offer_file_path
        offer_file = self.fetch_json_file(url)
        return offer_file

    def parse_offer_file(self, offer_file):
        publication_date = offer_file['publicationDate']
        flavor_info = {}
        for sku in list(offer_file['terms']['OnDemand'].keys()):
            for offer_term in list(offer_file['terms']['OnDemand'][sku].keys()):
                for rate_code in list(offer_file['terms']['OnDemand'][sku][offer_term]['priceDimensions'].keys()):

                    attributes = offer_file['products'][sku]['attributes']
                    flavor = {
                        'vcpu': attributes.get('vcpu'),
                        'memory': attributes.get('memory'),
                        'storage': attributes.get('storage'),
                        'clock_speed': attributes.get('clockSpeed'),
                        'instance_type': attributes.get('InstanceType'),
                        'price': float(offer_file["terms"]["OnDemand"][sku][offer_term]['priceDimensions'][rate_code][
                                           'pricePerUnit']['USD']),
                        'additional_info': [
                            offer_file['products'][sku],
                            offer_file["terms"]["OnDemand"][sku][offer_term]
                        ]
                    }
                    flavor_info[rate_code] = flavor
        return flavor_info


if __name__ == "__main__":
    flavors = AwsFlavor()
    flavors.update()
    print(flavors.get())
    # from cloudmesh.common.Shell import Shell
    # r = Shell.execute('cms flavor list --refresh')
