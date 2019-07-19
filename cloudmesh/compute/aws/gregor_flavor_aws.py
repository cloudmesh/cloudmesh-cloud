import  requests
from cloudmesh.common.util import writefile, readfile
from cloudmesh.common3.Shell import Shell
from pprint import pprint
from cloudmesh.common3.Benchmark import Benchmark
from textwrap import dedent
from bs4 import BeautifulSoup
from cloudmesh.common.util import banner

class AwsImages(object):

    def __init__(self):
        self.html = self.fetch()
        self.data = self.extract_tables(self.html)

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

    def print(self):
        for kind in self.data:
            banner(f"Table {kind}")
            pprint (self.data[kind])

    def pprint(self):
        banner('pprint')
        pprint(all)

if __name__ == "__main__":
     images = AwsImages()
     images.print()
     images.pprint()


