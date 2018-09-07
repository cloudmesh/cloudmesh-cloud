cm resource add .... [-inventory ~/cloudmesh/cloudmesh.yaml] < default

cm resource list

cm resource remove 


cm run --name NAME script.sh 

cm run --label LABEL script.sh

cm run LABELORNAME script.sh

```
cm run script.sh 1
cm run script.sh 2
cm run script.sh 3
cm run script.sh 4
cm run script.sh 5
cm run script.sh 6
```

> goes intoa  que and than we use the yaml to distribute through some mechanism onto a machine

```
def get_computer():
   return rand (1..6)
```   
   
script.sh

```
#!/bin/sh
echo $1 
hostname
uname -a
```

maintin a queue or map so that you know wher what hs to be executed

queue:
script.sh 1
script.sh 2
script.sh 3
script.sh 4
script.sh 5
script.sh 6


os.sytsem("script.sh 1")

```
from subprocess import check_output
out = check_output(["script.sh", "1"]).decode("utf-8").split("\n")
out = check_output(["script.sh", "1"]).splitlines()
#  splitlines, better, but still in binary, so you need to convert from binary each part of the array to utf-8


```


