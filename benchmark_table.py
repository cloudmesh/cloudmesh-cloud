import sys

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import readfile
from tabulate import tabulate

filename = sys.argv[1]

lines = readfile(filename).splitlines()
# print (lines)

result = Shell.find_lines_with(lines, "#csv")

table = []
for line in result:
    values = line.split(",")
    table.append([values[1],
                  values[2],
                  values[6],
                  values[7],
                  values[8]
                  ]
                 )

# pprint(table)

print(tabulate(table, tablefmt="grid"))
