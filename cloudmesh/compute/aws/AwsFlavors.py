import boto3
import json
from cloudmesh.common.console import Console
from progress.bar import Bar

class AwsFlavor:

    def __init__(self,
                 session,
                 region_name = "us-east-1",
                 **kwargs):
        self.session = session
        self.client = self.session.client('pricing', region_name = region_name)
        pass

    def fetch(self,
              url=None,
              offer='AmazonEC2',
              # n_results = None,
              n_results = 152,
              page_size = 100,
              filter = []
              ):

        results = []
        next_token = ''

        filterx = [
            {
            'Type': 'TERM_MATCH',
            'Field': 'instancesku',
            'Value': '3MFG4YWWT6SPWHET'
            }
        ]

        while next_token is not None and len(results) < n_results:
            if n_results and page_size > n_results - len(results):
                page_size = n_results - len(results)
            response = self.client.get_products(
                ServiceCode = 'AmazonEC2',
                MaxResults = page_size,
                FormatVersion = 'aws_v1',
                NextToken = next_token,
                Filters = filterx
            )
            # Add new price elements to results
            results.extend([json.loads(x) for x in response['PriceList']])
            if 'NextToken' in response.keys():
                next_token = response['NextToken']
            else:
                next_token = None

        return results

    @staticmethod
    def parse_aws_json(json):
        """
        To be run on a single json entry returned by the Amazon EC2 Pricing API
        """
        parsed = []
        for x in list(json['terms']['OnDemand'].keys()):
            for y in list(json['terms']['OnDemand'][x]['priceDimensions'].keys()):
                parsed.append({
                    "name": json['terms']['OnDemand'][x]['priceDimensions'][y].get('rateCode'),
                    "vcpu": int(json['product']['attributes'].get('vcpu')),
                    "memory": json['product']['attributes'].get('memory'),
                    "storage": json['product']['attributes'].get('storage'),
                    "clockSpeed": json['product']['attributes'].get('clockSpeed'),
                    "instanceType": json['product']['attributes'].get('instanceType'),
                    "os": json['product']['attributes'].get('operatingSystem'),
                    "price": float(json['terms']['OnDemand'][x]['priceDimensions'][y]['pricePerUnit'].get('USD')),
                    "metadata": json
                })
        return parsed

    def list(self, json_string_list):

        bar = Bar('Processing Flavor Products', max=len(json_string_list))

        flavors = []

        for s in json_string_list:
            flavors.extend(self.parse_aws_json(s))
            bar.next()

        bar.finish()

        return flavors


