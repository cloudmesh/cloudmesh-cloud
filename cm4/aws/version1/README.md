# AWS cm 

:o: what is the difference between this readme and the readme in the
directory above? Please only maintaine one README.

The project code is designed for using awscm.py to access the aws instance and run scripts in it.

In the code, we provide these commands for achieving the goal of conducting benchmarks on remote machines.

## Code Description

In the awscm folder, there are several basic python files:

### cloudmesh.yaml

This file contains the property of each instance, especially the AWS instance. In AWS cm project, we only concern about the block of 
information in "cloud" part. 

In the properties of one aws instance, we need users to specify the "name" and "label" of the instance. In the "credentials" part,
we need users to fill in the "KEY" and "ID". Make sure there are no duplicated names and labels in the "aws" list.

### awscm.py

The [`awscm.py`] is the main runable python class to start the aws cm project. It used the "docopt" to build the usage of commands.
Here are the version 1 commands that could be used:
___

```
  awscm.py resource add <yaml_file>
```
add extra instance information into the default yaml file. Please follow the schema of the asw instance. For example:

```
aws_a:
    credentials: {EC2_ACCESS_ID: "id", EC2_SECRET_KEY: "key"}
    label: aws_a
    name: aws_a
```
___
```
  awscm.py resource list [--debug]
```
list all instances from the default yaml file
___
```
  awscm.py resource remove <label_name>
```
remove the named or labeled instance from yaml file. Please fill in the correct name or label. For example:
```
  python awscm.py resource remove aws_a
```
___
```
  awscm.py resource view <label_name>
```
view named or labeled instance from the default yaml file. Please fill in the correct name or label. For example:
```
   python awscm.py view aws_a
```
___
```
  awscm.py copy instance <label_name> file <file> to <where> 
```
copy the file from local to the directory of instance. For exmaple:
```
  python awscm.py copy instance aws_a file test.txt to /test/
```
___
```
  awscm.py copy instance <label_name> foler <foler> to <where> 
```
copy the folder from local to the directory of instance. For example:
```
  python awscm.py copy instance aws_a folder /test/ to /test/
```
___
```
  awscm.py list instance <label_name> from <where>
```
list the files/folders in the directory of instanace. For example:
```
  python awscm.py instance aws_a from /test/
```
___
```
  awscm.py delete instance <label_name> file <file> from <where> 
```
delete the file from the directory of instance. For example:
```
  python awscm.py delete instance aws_a file text.txt from /test/
```
___
```
  awscm.py delete instance <label_name> folder <folder> from <where>
```
delete the folder from the directory of instance. For example:
```
  python awscm.py delete instance aws_a folder test from /test/
```
___
```
  awscm.py create instance <label_name> folder <folder> in <where>
```
create a new folder in the directory of instance. For example:
```
  python awscm.py create instance aws_a folder test in /test/
```
___
```
  awscm.py read instance <label_name> file <file> from <where>
```
read the file in the directory of instance. For example:
```
  python awscm.py read instance aws_a file test.txt from /test/
```
___
```
  awscm.py download instance <label_name> file <file> from <where> to <local>
```
download the file from the directory of instance to local. For example:
```
  python awscm.py download instance aws_a file test.txt from /test/ to /test/
```
___
```
  awscm.py download instance <label_name> folder <folder> from <where> to <local>
```
download the folder from the directory of instance to local. For example:
```
  python awscm.py download instance aws_a folder test from /test/ to /test
```
___
```
  awscm.py check instance <label_name> process_name <process>
```
check the running process in the instance. For example:
```
  python awscm.py check isntance aws_a process_name test
```
___
```
  awscm.py run instance <label_name> local <scripts>
```
run the scripts from local into the instance. For example:
```
  python awscm.py instance aws_a local test.sh,test.sh,test.sh
```
___
```
  awscm.py run instance <label_name> remote <scripts>
```
run the scripts from remote instance. For example:
```
  python awscm.py run instance aws_a remote test.sh,test.sh,test.sh
```
___
```
  awscm.py run local <scripts>
```
run the scripts from local into the random parallel instance. For example:
```
  python awscm.py run local test.sh,test.sh,test.sh
```
___
```
  awscm.py run remote <scripts>
```
run the scripts from the remote parallel instances. Make sure all instances have the required scripts. For example:
```
  python awscm.py run remote test.sh,test.sh,test.sh
```
___
```
  awscm.py run advanced <string>
```
this command is running the advanced algorithm. Developing a string based formulation of the tasks while providing the task in a def and using the chars | for parallel, ; for sequential and + for adding results.
In the project, we only develop simples string to be executed via ssh on a remote machines. The default setting is running the local scripts into remote parallel instances. 

For example, we define the function in [`advanced.py`]:
```
  def a():
  def b():
  def c():
  def d();
```
then we run the command to get the result:
```
  python awscm.py advanced a|b|c;d;a+b+c+d
```
___

### config.py

This python class is helping the project read the configuration of instances. In the yaml file, we set three types of instances: 
cloud, cluster and default, and the [`config.py`] could return relative block information of them.

### resource.py

[`resource.py`] is used to read and manage the default yaml file. In the class, we provides the read, update, add, remove and review functionalities for yaml file. And [`awscm.py`] would call these functions
to run the commands.

### utility.py

The [`utility.pt`] file contains the functions to do preparation before running scripts in remote instance. In this python class, we implement the functions:
copy file to instance, copy folder into instance, list files from the instance, delete file from instance, delete folder from instance, 
create folder instance, read file from instance, download file from instance, download folder from instance and check whether the process is running or not.

### run.py

The [`run.py`] file contains the functions to call the scripts in remote instance. In this class, we provides three functions: run the scripts locally to the instance,
 run the remote scripts in the instance and run the scripts in parallel instances.

### advanced.py

This class is used for the advanced approach to run a string based formulation of the tasks. Need to be updated later.

## TODO - Spark

- [ ] update more functionalities
- [ ] try the Spark in AWS instances
- [ ] try Spark by using awscm python code
- [ ] develop the test code
