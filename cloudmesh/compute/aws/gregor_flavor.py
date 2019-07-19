import  requests
from cloudmesh.common.util import writefile, readfile

def fetch():
    url='https://www.ec2instances.info'
    r = requests.get(url)
    print (r)
    writefile("gregor_flavor.txt", r.content.decode("utf-8"))

def read():
    content = readfile("gregor_flavor.txt")
    return content



#fetch()
content = read().split("\n")
print (content)

output = False

for line in content:
    if "var _pricing" in line:
        output = True
    if "function get_pricing()" in line:
        output = False

    if output:
        print (line)
