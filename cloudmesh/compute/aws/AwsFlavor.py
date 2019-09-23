import requests
from cloudmesh.common.console import Console
from progress.bar import Bar

class AwsFlavor(object):

    def __init__(self):
        pass

    def fetch(self):
        offer_file = self.fetch_offer_file()
        d = self.list(offer_file)
        return d

    @staticmethod
    def fetch_json_file(url):
        Console.msg(f"fetch: {url}")
        r = requests.get(url)
        return r.json()

    @classmethod
    def fetch_offer_file(
            cls,
            url=None,
            region="us-east-1",
            offer='AmazonEC2'
            ):
        if url is None:
            offer_index_url = f"https://pricing.{region}.amazonaws.com/offers/v1.0/aws/index.json"
            offer_index = cls.fetch_json_file(offer_index_url)
            offer_file_api_url = f"https://pricing.{region}.amazonaws.com"
            region_file_path = offer_index['offers'][offer]['currentRegionIndexUrl']
            regions_url = offer_file_api_url + region_file_path
            regions_file = cls.fetch_json_file(regions_url)
            offer_file_path = regions_file["regions"][region]["currentVersionUrl"]
            url = offer_file_api_url + offer_file_path
        offer_file = cls.fetch_json_file(url)
        return offer_file

    @classmethod
    def list(cls, offer_file):
    # Splitting the fetch and parse steps because the AWS EC2 File is large,
    # and splitting the operations logically makes it easier to test.
        publication_date = offer_file['publicationDate']
        flavor_info = {}
        bar = Bar('Processing Flavors', max=len(offer_file['terms']['OnDemand'].keys()))
        for sku in list(offer_file['terms']['OnDemand'].keys()):
            for offer_term in list(offer_file['terms']['OnDemand'][sku].keys()):
                for rate_code in list(offer_file['terms']['OnDemand'][sku][offer_term]['priceDimensions'].keys()):
                    flavor = {
                        'name': rate_code,
                        'vcpu': offer_file['products'][sku]['attributes'].get('vcpu'),
                        'memory': offer_file['products'][sku]['attributes'].get('memory'),
                        'storage': offer_file['products'][sku]['attributes'].get('storage'),
                        'clock_speed': offer_file['products'][sku]['attributes'].get('clockSpeed'),
                        'instance_type': offer_file['products'][sku]['attributes'].get('InstanceType'),
                        'price':float(offer_file["terms"]["OnDemand"][sku][offer_term]['priceDimensions'][rate_code]['pricePerUnit']['USD']),
                        'os': offer_file['products'][sku]['attributes'].get('operatingSystem'),
                        'additional_info': [
                            offer_file['products'][sku],
                            offer_file["terms"]["OnDemand"][sku][offer_term]
                        ]
                    }
                    flavor_info[rate_code] = flavor
            bar.next()
        bar.finish()
        return flavor_info
