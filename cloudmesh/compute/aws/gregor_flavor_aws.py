import  requests
from cloudmesh.common.util import writefile, readfile
from cloudmesh.common3.Shell import Shell
from pprint import pprint
from cloudmesh.common3.Benchmark import Benchmark
from textwrap import dedent
from bs4 import BeautifulSoup
from cloudmesh.common.util import banner
import pandas as pd
from collections import OrderedDict
from datetime import date
from cloudmesh.common.parameter import Parameter
from tabulate import tabulate


class AwsImages(dict):

    def __init__(self):
        self.html = self.fetch()
        self.__dict__ = self.extract_tables(self.html)

    def fetch(self):
        url='https://aws.amazon.com/ec2/instance-types/'
        r = requests.get(url)
        return r.content.decode("utf-8")

    def extract_tables(self, html):
        html = html.replace("<th", "<td")
        html = html.replace("vCPU*", "vCPU")

        soup = BeautifulSoup(html, features="lxml")

        REMOVE_ATTRIBUTES = ['style',
                             'height',
                             'width',
                             'border',
                             'cellpadding',
                             'cellspacing']
        for attribute in REMOVE_ATTRIBUTES:
            for tag in soup.find_all(attrs={attribute: True}):
                del tag[attribute]

        TAGS = ['b', 'i', 'u']
        for tag in TAGS:
            for match in soup.findAll(tag):
                match.replaceWithChildren()


        tables = soup.findAll("table")

        all = {}
        for table in tables:
             if table.findParent("table") is None:
                 print()
                 content = str(table)
                 #pretty = BeautifulSoup(content).prettify()
                 #print(pretty)
                 # print (content)

                 output = []
                 table_rows = table.find_all('tr')
                 for tr in table_rows:
                     td = tr.find_all('td')
                     row = [i.text.strip() for i in td]
                     output.append(row)
                 kind = output[1][0].split(".",1)[0]
                 all[kind] = output

        return all

    def print(self, key=None):
        if key == None:
            kinds = self.keys()
        else:
            keys = Parameter.expand(key)

        for kind in kinds:
            banner(f"Table {kind}")
            pprint (self.__dict__[kind])

    def pprint(self, key=None):
        if key == None:
            output = self.__dict__
            kind = "all"
        else:
            keys = Parameter.expand(key)
            output = {}
            for kind in keys:
                output[kind] = self.__dict__[kind]

        banner(f"Table {kind}")
        pprint(output)

    def keys(self):
        return list(self.__dict__.keys())

    def __getitem__(self, item):
        return self.__dict__.__getitem__(item)

    def table(self, key, output="fancy_grid"):
        """
        Available formats:

            "df"
            "plain"
            "simple"
            "github"
            "grid"
            "fancy_grid"
            "pipe"
            "orgtbl"
            "jira"
            "presto"
            "psql"
            "rst"
            "mediawiki"
            "moinmoin"
            "youtrack"
            "html"
            "latex"
            "latex_raw"
            "latex_booktabs"
            "textile"

        :param key:
        :param output:
        :return:
        """
        if key == None:
            kinds = self.keys()
            raise NotImplementedError
        else:
            keys = Parameter.expand(key)
            if len(keys) > 1:
                raise NotImplementedError
            # this is not fully implemented


        # Step 1. merge the table with keys

        # to be implemented

        # Step 2. print the resulting table

        #
        # For now we just print one table to demo
        # principal

        table = self.__dict__[key]
        pprint(table)
        df = pd.DataFrame.from_records(table[1:], columns=table[0])
        if output == 'df':
            return df
        else:
            return tabulate(df,
                       headers='keys',
                       tablefmt=output,
                       showindex="never")


if __name__ == "__main__":
    images = AwsImages()
    images.print()
    images.pprint()
    keys = images.keys()
    print ("Keys", keys)
    print ("Image")
    print ("III", images["a1"])

    print(images.table("a1"))
    print(images.table("a1", output="grid"))
