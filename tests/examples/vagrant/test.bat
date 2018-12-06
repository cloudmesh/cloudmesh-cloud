
:: setup	
set EHVAGRANT_HOME=.

:: default vagrantfile
python ../vagrant.py vagrant ls

:: create vagrantfile
python ../vagrant.py vagrant create --vms=master,slave
python ../vagrant.py vagrant ls

:: start up
python ../vagrant.py vagrant start
python ../vagrant.py vagrant ls

:: suspend
python ../vagrant.py vagrant suspend
python ../vagrant.py vagrant ls

:: resume
python ../vagrant.py vagrant resume
python ../vagrant.py vagrant ls

:: info
python ../vagrant.py vagrant info master


:: upload
:::: test senario - mutiple mahicne, upload file/folder
echo "both data" > both.txt
mkdir test_folder
echo "both data in the folder" > test_folder/both_in_folder.txt
python ../vagrant.py vagrant upload --from=both.txt --to=~
python ../vagrant.py vagrant upload --from=test_folder --to=~ -r

:: run commmand
:::: test senario - single machine
python ../vagrant.py vagrant run command "ls ~" --vms=master
:::: test senario - multiple machine
python ../vagrant.py vagrant run command "ls ~/test_folder"


:: run script 
:: test senario - run single machine, upload folder, download folder
echo master data > test_folder/test_data.txt
python ../vagrant.py vagrant run script script.sh --data test_folder/ --vms=master
tree ./experiment/master /F

:: test senario - run single machine, upload file, download file
python -c "out=open('script2.sh', 'wb'); out.write('mkdir \"${1}\"/output\x0Acat \"${1}\"/data/slave.txt > \"${1}\"/output/output.txt'.encode('utf8')); out.close()"
echo slave data > slave.txt
python ../vagrant.py vagrant run script script2.sh --data slave.txt/ --vms=slave
tree ./experiment/slave /f

:: test senario - run multiple machine, upload folder, download folder
echo both data > test_folder/test_data.txt
python ../vagrant.py vagrant run script script.sh --data test_folder
tree ./experiment /F

:: test senario - run multiple machine, upload file, no download
echo|set /p="cat ${1}/data/both.txt">script3.sh
python ../vagrant.py vagrant run script script3.sh --data both.txt 



:: download

:: test senario - run mutiple machine, download file to folder
python ../vagrant.py vagrant download --from=~/both.txt --to=./experiment/new.txt
tree ./experiment /F

:: test senario - run multiple machine, upload file, no download
python ../vagrant.py vagrant download --from=~/test_folder/ --to=./experiment -r 
tree ./experiment /F

:: stop
python ../vagrant.py vagrant stop
python ../vagrant.py vagrant ls

:: destory
python ../vagrant.py vagrant destroy -f 
python ../vagrant.py vagrant ls

:: cleanup
del both.txt
del slave.txt
del script2.sh
del script3.sh
del *.log
del Vagrantfile
rd experiment /s /q
rd test_folder /s /q

