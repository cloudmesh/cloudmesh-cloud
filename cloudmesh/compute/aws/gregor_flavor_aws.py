import  requests
from cloudmesh.common.util import writefile, readfile
from cloudmesh.common3.Shell import Shell
from pprint import pprint
from cloudmesh.common3.Benchmark import Benchmark
from textwrap import dedent
from bs4 import BeautifulSoup

def fetch():
    url='https://aws.amazon.com/ec2/instance-types/'
    r = requests.get(url)
    print (r)
    writefile("gregor_flavor_aws.html", r.content.decode("utf-8"))

def read():
    content = readfile("gregor_flavor_aws.html")
    return content


input = read()
soup = BeautifulSoup(input, features="lxml")

REMOVE_ATTRIBUTES = ['style', 'height', 'width', 'border', 'cellpadding',
'cellspacing']
for attribute in REMOVE_ATTRIBUTES:
    for tag in soup.find_all(attrs={attribute: True}):
        del tag[attribute]

TAGS = ['b', 'i', 'u']
for tag in TAGS:
    for match in soup.findAll(tag):
        match.replaceWithChildren()


tables = soup.findAll("table")

for table in tables:
     if table.findParent("table") is None:
         content = str(table)
         #pretty = BeautifulSoup(content).prettify()
         #print(pretty)
         print (content)
