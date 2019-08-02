from cloudmesh.configuration.Config import Config
import contextlib
import urllib.request
import json

class AWSflavor(flavor):

    def __init__(self):
        pass

    def get(self):
        output = []
        for key in self.__dict__:
            output.append(self.__dict__.get(key))
        return output

    def update(self, dict = {}):
        # Note that dict is overwritten, and will be ignored
        offer_file = self.fetch_offer_file()
        dict = self.parse_offer_file(offer_file)
        self.__dict__ = dict

    @staticmethod
    def fetch_json_file(url):
        with urllib.request.urlopen(url) as req:
            data = json.loads(req.read().decode())
            return data

    def fetch_offer_file(
            self, 
            url = None,
            region = "us-east-1"
    ):
        if url is None:
            offer_index_url = f"https://pricing.{region}.amazonaws.com/offers/v1.0/aws/index.json"
            offer_index = self.fetch_json_file(offer_index_url)
            offer_file_api_url = f"https://pricing.{region}.amazonaws.com"
            # offer_file_path = offer_index['offers']['AmazonEC2']['currentVersionUrl']
            region_file_path = offer_index['offers']['AmazonEC2']['currentRegionIndexUrl']
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
                    flavor = {
                        'vcpu': offer_file['products'][sku]['attributes'].get('vcpu'),
                        'memory': offer_file['products'][sku]['attributes'].get('memory'),
                        'storage': offer_file['products'][sku]['attributes'].get('storage'),
                        'clock_speed': offer_file['products'][sku]['attributes'].get('clockSpeed'),
                        'instance_type': offer_file['products'][sku]['attributes'].get('InstanceType'),
                        'price':float(offer_file["terms"]["OnDemand"][sku][offer_term]['priceDimensions'][rate_code]['pricePerUnit']['USD']),
                        'additional_info': [
                            offer_file['products'][sku],
                            offer_file["terms"]["OnDemand"][sku][offer_term]
                        ]
                    }
                    flavor_info[rate_code] = flavor
        return flavor_info


if __name__ == "__main__":
    flavors = AWSflavor()
    flavors.update()
    print(flavors.get())
    from cloudmesh.common.Shell import Shell
    r = Shell.execute('cms flavor list --refresh')
