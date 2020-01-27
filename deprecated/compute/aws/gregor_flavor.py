import re
from pprint import pprint

import pandas as pd
import requests
from bs4 import BeautifulSoup
from cloudmesh.common.util import banner
from tabulate import tabulate


class AwsImages(object):

    def __init__(self):
        self.html = self.fetch()
        self.data = self.extract_tables(self.html)

    def fetch(self):
        url = 'https://www.ec2instances.info'
        r = requests.get(url)
        return r.content.decode("utf-8")

    def extract_tables(self, html):
        html = html.replace("<th", "<td")
        html = html.replace("vCPU*", "vCPU")

        soup = BeautifulSoup(html, features="lxml")

        # noinspection PyPep8Naming
        REMOVE_ATTRIBUTES = ['style',
                             'height',
                             'width',
                             'border',
                             'cellpadding',
                             'cellspacing']
        for attribute in REMOVE_ATTRIBUTES:
            for tag in soup.find_all(attrs={attribute: True}):
                del tag[attribute]

        # noinspection PyPep8Naming
        TAGS = ['b', 'i', 'u']
        for tag in TAGS:
            for match in soup.findAll(tag):
                match.replaceWithChildren()

        table = soup.find("table")

        output = []

        table_rows = table.find_all('tr')
        for tr in table_rows:
            td = tr.find_all('td')
            # noinspection PyPep8
            row = [re.sub('\s+', ' ', i.text).strip() for i in td]
            output.append(row)

        return output

    def print(self):
        banner(f"Table")
        pprint(self.data)

    def pprint(self):
        banner(f"Table")
        pprint(self.data)

    def table(self, output="fancy_grid"):
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

        table = self.data
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
    from cloudmesh.common.StopWatch import StopWatch

    StopWatch.start("convert aws image table")
    images = AwsImages()
    # images.print()
    # images.pprint()
    # keys = images.keys()
    # print ("Keys", keys)
    # print ("Image")

    output = images.table()
    StopWatch.stop("convert aws image table")
    print(output)

    StopWatch.benchmark()
