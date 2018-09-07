cm resource add .... [-inventory ~/cloudmesh/cloudmesh.yaml] < default

cm resource list

cm resource remove 


cm run --name NAME script.sh 

cm run --label LABEL script.sh

cm run LABELORNAME script.sh

cm run script.sh 1
cm run script.sh 2
cm run script.sh 3
cm run script.sh 4
cm run script.sh 5
cm run script.sh 6

> goes intoa  que and than we use the yaml to distribute through some mechanism onto a machine

def get_computer():
   return rand (1..6)
   
   
script.sh

#!/bin/sh
echo $1 
hostname
uname -a





