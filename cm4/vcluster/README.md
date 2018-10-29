# Parallel Remote Jobs

This is a tool to submit jobs to remote hosts in parallel:

```console
$ ./submit_jobs.py
usage: submit_jobs.py [-h] [--CProcNum Num] [--suffix suffix] [--nometa]
                      [--nodownload] [--download metapath]
                      ConfPath ProcNum

Running remote parallel jobs

positional arguments:
  ConfPath             Path of configuration file
  ProcNum              Number of processes

optional arguments:
  -h, --help           show this help message and exit
  --CProcNum Num       Number of processes used for collecting the results.
                       (default: 1)
  --suffix suffix      suffix to be added to output file names. (default:
                       _20181021_23174972)
  --nometa             If used, the metadata will not be saved (warning:
                       results cannot be collected later). (default: False)
  --nodownload         If used, the result will not be downloaded (cannot be
                       used with --nometa flag) (default: False)
  --download metapath  Retrieve the result from a previously submitted job
                       using its metadata file. (default: None)
```

The two mandatory arguments are `ConfPath` defining the path of the configuration file and `ProcNum` which indicates the number of process that will be used to submit the jobs. The optional argument `CProcNum` defines the number of processes that will be used for collecting the results. The `suffix` can be used for distinguishing several instances of the same runs on same set of nodes and the `nometa` flag is in case the user does not want to keep the metadata. The metadata can be later used for retrieving the results that needs a lot of time to run and you do not want to let the script run for that amount of time. For this purpose, the `--nodownload` argument should be used, indicating the script is not expected to wait for the results to be downloaded. When later on you wanted to download the results, you can use the `--download` argument followed by the path of the metadata file. This is a sample usage of this tool:

```console
$ ./submit_jobs.py config_file.ini 4
Remote Pid on NODE4: 29418
Remote Pid on NODE3: 29422
Remote Pid on NODE1: 20616
Remote Pid on NODE2: 20619
Remote Pid on NODE5: 20841
collecting results
Results from NODE1 collected
Results from NODE2 collected
Results from NODE5 collected
waiting for other results...
Results from NODE3 collected
Results from NODE4 collected
waiting for other results...
All of the remote results collected
```

An example of a parallel run with its results being downloaded later would be as follows:
```console
$ ./submit_jobs.py config_file.ini 5 --nodownload
Remote Pid on NODE1: 3449
Remote Pid on NODE5: 3557
Remote Pid on NODE2: 3564
Remote Pid on NODE3: 20062
Remote Pid on NODE4: 20067
metadata saved.
$
$
$ ./submit_jobs.py config_file.ini 1 --download metadata/md_20181021_23152131.pkl
collecting results
Results from NODE1 collected
Results from NODE2 collected
Results from NODE3 collected
Results from NODE4 collected
Results from NODE5 collected
waiting for other results if any...
All of the remote results collected.
```

### Configuration file

The information of the nodes should be provided to the tool using a configuration file.


This is an example of configuration file with two nodes:

```
[NODE1]
    hostname=machine1
    sshconfigpath=~/vms/ubuntu14/sshconfig1
    script_path=./input/test_script_filein_fileout.sh
    remote_path=~/
    arg_type=params+file
    arg_params=test-script-argument
    arg_file_path=./input/test-script-argument
    output_type=file
    output_filename=test-script-output
    local_output_path=./output
[NODE2]
    hostname=machine2
    sshconfigpath=~/vms/ubuntu14/sshconfig2
    script_path=./input/inf_script_stdin_fileout.sh
    remote_path=~/
    arg_type=params
    arg_params=
    output_type=file
    output_filename=outie.out
    local_output_path=./output
```
### Nodes and Script

This example is defining two nodes for the tools, namely `NODE1` and `NODE2` where the `hostname` of the former is `machine1` and the `hostname` of the latter is `machine2`.

Note   that for security purposes this tool does not get remote credentials, and connects to remote nodes with ssh keys. The path for the ssh configuration files is defined in `sshconfigpath`.

The **local**  location of a script/program to be executed on a remote node is defined using `script_path` parameter. This script will be copied and executed from the remote path which is define using the `remote_path` parameter.

### Script Input

This tool assumes that the input is always via command line argument where the script might or might not need another file as input. These are distinguished using the `arg_type` parameter where `arg_type=params` indicates that the input of the program is only command line arguments with no additional file and  `arg_type=params+file` indicates both arguments and additional input file. In both cases, the `arg_params` attribute is required where the input arguments can be defined. However, in case of `arg_type=params+file`, an additional parameter should be added, namely `arg_file_path` where the path to the input file should be defined.  Note that in the remote nodes, the input file will be placed in the same path as the target script.

For instance, Suppose a program is expected to be run using the following command:

```console
$ ./programX A B C
```

In this case, the `arg_type` and `arg_params` should be defined as :
```
arg_type=params
arg_params=A B C
```
As for the other case, suppose the `programY` takes a file as input too:
```console
$ ./programX A B -F ~/inputs/inputFile
```
In this case the required parameters should be defined as:
```
arg_type=params
arg_params=A B -F ./inputFile
arg_file_path=~/inputs/inputFile
```
It is indeed possible to run a program without extra arguments:
```console
$ ./programZ
```
This case can be defined by leaving the `arg_params` attribute empty:
```
arg_type=params
arg_params=
```

### Script Output

The program assumes that the output of the target program could be in the following forms:

1. Printed information in the standard output indicated using `output_type=stdout`.
2. A file which is reflected in the  configuration file using: `output_type=file`.
3. Both a file and printed information in standard output indicated using `output_type=file+stdout`.

 In all of the above-mentioned cases, you should add another parameter called `local_output_path` which defines the **local** path in which the results will be copied. Also note that in case 2 and 3, you are required to add an additional parameter, namely `output_filename`, which tells the program what is the name of the expected output file in remote.

 As an example, consider a program that prints some debug information in the standard output as well as produces a file named `output.txt`:

 ```console
$ ./program
INFO: Linux vagrant-ubuntu-trusty-64 3.13.0-160-generic #210-Ubuntu SMP Mon Sep 24 18:08:15 UTC 2018 x86_64 x86_64 x86_64 GNU/Linux

File saved as output.txt
 ```
 This should be reflected in the configuration file as:

 ```
 output_type=stdout+file
 output_filename=output.txt
 local_output_path=./output
 ```
