import boto3
import copy
import json
import re
from cloudmesh.common.console import Console
from progress.bar import Bar
from pprint import pprint

class AwsFlavor:

    # Changes need to be made in the provider and test files to make use of the
    # new api fetching features, namely to reduce the number of elements
    # fetched, so tests take less time.
    # See Commit 1907ec2 for an example implementation

    def __init__(self,
                 session,
                 region_name = "us-east-1",
                 **kwargs):
        self.session = session
        self.client = self.session.client('pricing', region_name = region_name)
        pass

    def fetch(self,
              n_results=float("inf"),
              url=None,
              offer='AmazonEC2',
              page_size = 100,
              **query
              ):

        results = []
        next_token = ''

        if query == {}:
            query = None
        elif isinstance(query, dict):
            query = [query]

        while next_token is not None and len(results) < n_results:
            if n_results and page_size > n_results - len(results):
                page_size = n_results - len(results)
            if query is None:
                response = self.client.get_products(
                    ServiceCode = 'AmazonEC2',
                    MaxResults = page_size,
                    FormatVersion = 'aws_v1',
                    NextToken = next_token
                )
            else:
                response = self.client.get_products(
                    ServiceCode = 'AmazonEC2',
                    MaxResults = page_size,
                    FormatVersion = 'aws_v1',
                    NextToken = next_token,
                    Filters = query
                )
            # clean up rate codes.
            response_str = json.dumps(response)
            response_str = re.sub('([0-9A-Z]{16})\.', r'\1', response_str)
            response_str = re.sub('([0-9A-Z]{10})\.', r'\1', response_str)
            # Add new price elements to results
            response = json.loads(response_str)
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
        # flavor['terms']['OnDemand']['sku_offerTermCode']['priceDimensions']['sku_offerTerm_priceDimension']['pricePerUnit']['USD']
        parsed = []
        if 'OnDemand' in json['terms'].keys():
            for x in list(json['terms']['OnDemand'].keys()):
                for y in list(json['terms']['OnDemand'][x]['priceDimensions'].keys()):
                    json_tmp = copy.deepcopy(json)
                    name = json['terms']['OnDemand'][x]['priceDimensions'][y].get('rateCode')
                    name = name.replace(".", "")
                    json_tmp['name'] = name
                    json_tmp["sku"] = json['product'].get('sku')
                    json_tmp["sku_offerTermCode"] = x
                    json_tmp["sku_offerTerm_priceDimension"] = y
                    json_tmp["cm"] = {"kind": "flavor", "name": name, "cloud": "aws", "cloudtype": "aws"}
                    json_tmp['terms']['OnDemand']= {}
                    json_tmp['terms']['OnDemand']['sku_offerTermCode'] = copy.deepcopy(json['terms']['OnDemand'][x])
                    json_tmp['terms']['OnDemand']['sku_offerTermCode']['priceDimensions'] = {}
                    json_tmp['terms']['OnDemand']['sku_offerTermCode']['priceDimensions']['sku_offerTerm_priceDimension'] = copy.deepcopy(json['terms']['OnDemand'][x]['priceDimensions'][y])
                    parsed.append(json_tmp)
        if len(parsed) == 0:
            parsed = None
        return parsed

    def list(self, json_string_list):

        bar = Bar('Processing Flavor Products', max=len(json_string_list))

        flavors = []

        for s in json_string_list:
            flavor = self.parse_aws_json(s)
            if flavor is not None:
                flavors.extend(flavor)
            bar.next()

        bar.finish()
        return flavors

#    def PrintAWSFlavor()

#{
#    name:
#    cm:
#        kind: flavor
#        name: same as above
#        cloud: aws
#    product
#    publicationDate
#    serviceCode
#    version
#    terms
#        OnDemand
#}

##TODO: Implement Query in List
##TODO: Write Print for AWS Flavors, andapt Provider.Print
##TODO: Fix the parsing code to standardize the database entries

