import requests
from cloudmesh.common.console import Console
from progress.bar import Bar

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

price is something like

"price" : {
        "offerTermCode" : "JRTCKXETXF",
        "sku" : "DBCQPZ6Z853WRE98",
        "effectiveDate" : "2019-07-01T00:00:00Z",
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
                "appliesTo" : []
            }
        },
        "termAttributes" : {}
    },
"""


class AwsFlavor(object):

    def __init__(self):
        pass

    """
    def get(self):
        output = []
        for key in self.__dict__:
            output.append(self.__dict__.get(key))
        return output
    
    def update(self):
        offer_file = self.fetch_offer_file()
        d = self.parse_offer_file(offer_file)
        return d
    """

    @staticmethod
    def fetch_json_file(url):
        Console.msg(f"fetch: {url}")
        r = requests.get(url)
        return r.json()

        # with urllib.request.urlopen(url) as req:
        #    data = json.loads(req.read().decode())
        #    return data

    def fetch(self,
              url=None,
              region="us-east-1",
              offer='AmazonEC2'
              ):
        if url is None:
            offer_index_url = f"https://pricing.{region}.amazonaws.com/offers/v1.0/aws/index.json"
            offer_index = self.fetch_json_file(offer_index_url)
            offer_file_api_url = f"https://pricing.{region}.amazonaws.com"
            # offer_file_path = offer_index['offers']['AmazonEC2']['currentVersionUrl']
            region_file_path = offer_index['offers'][offer][
                'currentRegionIndexUrl']
            regions_url = offer_file_api_url + region_file_path
            regions_file = self.fetch_json_file(regions_url)
            offer_file_path = regions_file["regions"][region][
                "currentVersionUrl"]
            url = offer_file_api_url + offer_file_path

        offer_data = self.fetch_json_file(url)
        return offer_data

    def list(self, offer):

        bar = Bar('Processing Flavor Products', max=len(offer["products"]))

        flavors = {}

        #
        # locate metadata
        #
        metadata = {}
        for key in ["formatVersion",
                    "disclaimer",
                    "offerCode",
                    "version",
                    "publicationDate"]:
            metadata[key] = offer[key]

        #
        # Find Products
        #
        for key in offer["products"].keys():
            product = offer["products"][key]

            # try:
            #    product['name'] = product['attributes']['instanceType']
            # except:
            #    product['name'] = key

            product['name'] = key
            product.update(metadata)

            flavors[key] = product
            bar.next()

        bar.finish()

        bar = Bar('Processing Flavor Prices', max=len(offer["products"]))

        #
        # Manage terms for prices
        #
        terms = offer['terms']['OnDemand']

        for term, value in terms.items():
            bar.next()

            if len(value.keys()) != 1:
                print(value)
                raise ValueError("too many terms")
            _key = list(value.keys())[0]
            entry = value[_key]

            name = entry['sku']
            if term != entry['sku']:
                print(entry)
                raise ValueError("name and sku are different")

            # flavors[name]['prices'] = entry

            #
            # first price
            #

            prices = entry['priceDimensions']
            price_key = list(prices.keys())[0]
            price = prices[price_key]
            flavors[name]['price'] = price

        bar.finish()

        return [v for v in flavors.values()]
