import  requests
from cloudmesh.common.util import writefile, readfile
from cloudmesh.common3.Shell import Shell
from pprint import pprint
from cloudmesh.common3.Benchmark import Benchmark
from textwrap import dedent
from bs4 import BeautifulSoup

def fetch():
    url='https://aws.amazon.com/ec2/instance-types/'
    Benchmark.Start()
    r = requests.get(url)
    Benchmark.Stop()
    print (r)
    writefile("gregor_flavor_aws.html", r.content.decode("utf-8"))

def read():
    Benchmark.Start()
    content = readfile("gregor_flavor_aws.html")
    Benchmark.Stop()
    return content

#def pandoc(file, out):
#    Shell.run(command=f"pandoc {file} -o {out}")



def clean(content):
    Benchmark.Start()
    content = content.replace(' style="text-align: center;"', "")
    content = content.replace(' valign="middle"', "")
    content = content.replace('<span style="font-size: 12px;">', "")
    content = content.replace('</span>', "")
    content = content.replace('</b>', "")
    content = content.replace('<b>', "")
    content = content.replace('<br/>', "") # this seems not to work
    content = content.split("\n")

    #print (content)

    tables = []
    output = False
    for line in content:
        if "<table" in line:
            tmp = line.split("<table", 1)
            line = tmp[0] + "<table>"
            output = True
            table = ""
        if "</table" in line:
            output = False
            table = table + line.split("</table")[0] + "</table>"
            table = dedent(table)
            tables.append(table)
        if "<td " in line:
            prefix = line.split("<td ",1)[0]
            content = line.split(">",1)[1]
            line = prefix +"<td>" + content
        if "<th " in line:
            prefix = line.split("<th ", 1)[0]
            content = line.split(">", 1)[1]
            line = prefix + "<th>" + content

        if output:
            line.replace(' style="text-align: center;"', "")
            table = table + line + "\n"
    Benchmark.Stop()
    return tables

fetch()
content = read()
tables = clean(content)

pprint (tables)

for t in tables:
    if "<th" in t:
        soup = BeautifulSoup(t)

        table = soup.find('table')

        headers = [header.text for header in table.find_all('th')]
        results = [{headers[i]: cell for i, cell in enumerate(row.find_all('td'))}
                   for row in table.find_all('tr')]

        print (results)

Benchmark.print()
