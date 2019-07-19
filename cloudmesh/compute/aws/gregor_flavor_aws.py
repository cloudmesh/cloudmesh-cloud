import  requests
from cloudmesh.common.util import writefile, readfile
from cloudmesh.common3.Shell import Shell
from pprint import pprint
from cloudmesh.common3.Benchmark import Benchmark
from textwrap import dedent
from bs4 import BeautifulSoup
from cloudmesh.common.util import banner

def fetch():
    url='https://aws.amazon.com/ec2/instance-types/'
    r = requests.get(url)
    print (r)
    writefile("gregor_flavor_aws.html", r.content.decode("utf-8"))

def read():
    content = readfile("gregor_flavor_aws.html")
    return content



input = read()
input = input.replace("<th", "<td")


soup = BeautifulSoup(input, features="lxml")

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

for kind in all:
    banner(f"Table {kind}")
    pprint (all[kind])

pprint(all)


