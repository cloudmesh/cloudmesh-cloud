

# eh-vagrant: enhanced Vagrant python interface

[TOC]

----

## Introduction

Vagrant is a open-source software that help you to build and manage virtual machines through command line interface. `eh-vagrant`provide you an enhanced command line interface that enable users to utilize Vagrant functionality in an earlier way. To better grasp what is Vagrant, please refer to [Vagrant website](https://www.vagrantup.com/) . 

The major enhancement of `eh-vagrant` is that it enables you to execute the same job on multiple Vagrant instances at the same time, including:

- transfer file and folder between host machine and instances

- execute command or script on instances.

This allows you to test a program on multiple virtual machines, which may have different OS and working environment, at the same time, by just issuing a **single** command. 



-----

## Setup Walkthrough

### Requirement summary

Minimum  requirements to use`eh-Vagrant`with Vagrant are the following:

- A working Vagrant software work with appropriate [virtualization provider](#Install-*virtualization-provider*).
- Python 3  and `pip`should be available on the host machine.
- `scp` functionality should be available on the host machine.
- Currently, `en-Vagrant ` just support the virtual machine that are running an Unix-like OS, such as Ubuntu.

### Setup `eh-vagrant`  and its python dependencies

IMPORTANT: if you are using`eh-vagrnat` within `cloudmesh`, please refer to [here](#Using-`eh-vagrant`-with-`Cloudmesh`) to setup `eh-vagrant `.

Download or clone this project from github, unzip if needed, open your terminal and `cd` to the project root directory, and finally, execute `pip install -r requirement.txt` in your terminal. Wait `pip` to handle all of the work for you, and.... BOOM! You now have setup all of the python dependencies required for running `eh-vagrant`.

### Install vagrant

You can download Vagrant from [here](https://www.vagrantup.com/downloads.html). It supports all mainstream operating system, including Windows, Mac OS, and various Linux distribution.  After finishing installation, you can check if the installation success by executing `vagrnat version`.  You should see something like below.

![vagrant version](./img/version.png)

### Install *virtualization provider*

Although Vagrant *help* you with managing virtual machines, Vagrant itself does not *handle* the task of virtualization. Vagrant rely on virtualization software or even cloud service provider to do the actual work of *virtualization* -- running virtual machine on top of host machine, provisioning computational and storage resources to virtual machines, communicating between host and virtual machine....etc. In other word, to leverage Vagrant functionality**, you need to install Vagrant along with *virtualization provider* and/or the correspondent t *Vagrant plugin*** that enables Vagrant to interact with the virtualization provider.

The default virtualization provider of Vagrant is [VirtualBox](https://www.virtualbox.org/).  You don't have to install any plugin to let Vagrant working with VirtualBox. However, you indeed need to install VirtualBox by yourself if you don't have one on your host computer. In this case please refer to [VirtualBox downloand page](https://www.virtualbox.org/wiki/Downloads). Also, please note that using Virtual Box as the virtualization provider implies virtual machines will run on your host machine. So make sure there are sufficient resources on your host machine. 

You may choose other virtualization software or even cloud service provider as your virtualization provider. In this case, please setup virtualization provider and follow the [Vagrant user manual]('https://www.vagrantup.com/docs/providers/')  to setup Vagrant with correspondent plugin. If there is no special need that you have to address, we strongly recommend you just go with VirtualBox.

### Configure `Vagrantfile`

Vagrant will only interact with the virtual machines defined in the  `Vagrantfile`. `Vagrantfile` should be stored at`VAGRNATFILE_PATH`,  which default path is  `./vagrant_workspace/Vagrantfile` .

IMPORTANT: If you are using `eh-vagrant` with `cloudmesh`, then your `VAGRANTFILE_PATH` will be changed to  `$CLOUDMESH_ROOT_DIRECTORY$/configuration/Vagrantfile`.

`eh-vagrant` comes with a default `Vagrantfile` which defines two Ubuntu machine called `node1` and `node2`. However, with  `eh-vagrant`, you can easily setup your`Vagrantfile` by using the command [vagrant create](#create-instances). The following walkthrough assumes you go with the default `Vagrantfile`.

You can also try to detailed customize your own `Vagrantfile`. Please refer to [Vagrant user manual](https://www.vagrantup.com/docs/vagrantfile/) to see how to do that. Don't forget that currently `eh-vagrnat` just supports Unix-like OS, so define **your virtual machining running an Unix-like OS, or `eh-vagrant` will not function correctly**. After finishing your modification on `Vagrantfile`, save it at `VAGRANTFILE_PATH`, **otherwise it will not work with `eh-vagrant`**.  

### Initialize virtual machine

After finishing `Vagrantfile`definition,  you are now ready to deploy and run your virtual machine with Vagrant. But first, let us check current status of your Vagrant project. Execute `python vagrant.py vagrant status`at `eh-vagrant` root directory, you will see: 

![before_init](./img/before_init.png)

Then execute `python vagrant.py vagrant start`. Since your machines are not deployed yet, Vagrant will first deploy your machines and then bring them up, and automatically do LOTS of setting.  When Vagrant has done its work, we can confirm this by issuing `python vagrant.py vagrant status` again. You will see now:

![after_init](/img/after_init.png)

HOO-WA! Your two virtual machines are painlessly deployed, configured, up and running! Now you are ready to do some fancy work with Vagrant and `eh-vagrant`.

### Micellouenes: setup python 3 and `scp` on host machine

Since these topics are not directly relate to `eh-vagrant`, and many users may already have these functionally set up on their host machine,  here I just describe how do you check these functionally are working properly. 

For `scp`, open terminal and execute `scp`, you should see a short  usage guide show on your screen. If it is not there, please install `scp` and make sure its executive file is in your `PATH` environment variable. 

![scp_availability check](/img/scp.png)

For python 3,  open your terminal and execute `python--version`,  you should see python version number and distribution  show on your screen. If no related information shows up, or your python version is not `3.X`, please install correct python version.

![python_availability check](/img/python.png)

### Using `eh-vagrant` with `cloudmesh`

`eh-vagrant` was originally developed as a module of `cloudmesh`. If you get `eh-vagrant` with `cloudmesh` distribution,  do following change when setup `eh-vagrant` with `cloudmesh`:

- You DO NOT have to install python dependencies for`eh-vagrant` separately from `cloudmesh`.  When `cloudmesh` sets up, it automatically installs `eh-vagrant`'s  python dependencies.

- Your `VAGRANTFILE_PATH` now change to `$CLOUDMESH_ROOT_DIRECTORY$/configuration/Vagrantfile`.

- To enable `cloudmesh` to interact with Vagrant instance, add Vagrant instances' information to the configuration file of `cloudmesh`, which locates at `$CLOUDMESH_ROOT_DIRECTORY$/configuration/cloudmesh.yaml`. To specify a Vagrant instance in `cloudmesh.yaml`,  just fill the `name` of the Vagrant instance, and let `address` variable point to the `VAGRHANTFILE_PATH`. You may leave all other field blank. Here is an example to specify `node1`and `node2` in `cloudmesh.yaml`.


  ```yaml
  cloudmesh:
     cluster:
      cluster_vagrant:
        vagrant_a:                   
          name:                       node1
          label:                      
          address:                    ./Vagrantfile
          credentials:
            username:                 
            pulickey:                 
        vagrant_b:
          name:                       node2
          label:                      
          address:                    ./Vagrantfile
          credentials:
            username:                 
            pulickey:
  ```

------

## Functionality 

### Common behavior

- Commands will only affect the instances that belongs to *current Vagrant environment*, which is defined by the `Vagrantfile` locates at `VAGRNANTFILE_PATH`
 - For most of the commands, use`--vms` argument to specify which instances you want to work with. Specify instances by `name`. In most cases, it is possible to issue a command without `--vms`. Be careful.  Issuing a command without specifying instances will usually affect **all** of the instances available in  current vagrant environment.
 - Before transferring file and folder between host and instances or running commands and scripts on instances,  you must **make sure** that all of the instances you want to work with are **up,  running, and reachable through network .** 

### Manage instances

#### create instances

Usage: `python vagrant.py vagrant create VM_COUNT BOX_NAME`

Create `VM_COUNT` number of  instances with the image named `BOX_NAME`.  If you specify a `BOX_NAME` that is available on the host machine (i.e., the box names listed in `vagrant box list` command), Vagrant will create instances using the local image. Otherwise, it will try to search [Vagrant Cloud](https://app.vagrantup.com/boxes/search) and download the image which owns the same name.

#### start up instances

Usage :`python vagrant.py vagrant start [--vms=<vmList>]`

Start up stopped or suspended instances.

#### stop instances

Usage:`python vagrant.py vagrant stop [--vms=<vmList>]`

Shut down instances. Any unsaved data will be lost. 

#### suspend instance

Usage: `python vagrant.py vagrant suspend [--vms=<vmList>]`

Save current state of instances and then stop it. Unsaved data will not lost and user can restore the current state and continue to work latter on.

#### destroy instances

Usage:```python vagrant.py vagrant destroy [--vms=<vmList>]```

Destroy Vagrant instances. The data stored on the instance will be lost.

#### show current status of instances

Usage: `python vagrant.py vagrant info`

Show the status of all Vagrant instances belonging to the current environment. 

###  Transfer file and folder between host and instances

- The following functionality are implemented by utilizing `scp ` command. [As previously mentioned](#Micellouenes:-setup-python-3-and-`scp`-on-host-machine), please make sure `scp` functionality is available on your host machine.
- If you specify a folder as the target to be uploaded/downloaded, all of its contents will be get uploaded/downloaded.
- **To specify a folder, just put a `/` in the end of the path string**. For example, `A/smaple/path/string/`.  Or use `-r` flag to indicates the target is a folder. 

#### upload file or folder (from host to instances)

Usage:`python vagrant.py vagrnat upload --from FROM --to TO [-r] [--vms=<vmlist>]`

Upload file or folder on host machine to instances.

#### download file or folder (from instances to host)

Usage:`python vagrant.py vagrnat download --from FROM --to TO [-r] [--vms=<vmlist>]`

If  you are trying to download file or folder from two or more instances simultaneously,  data will be parallelly downloaded and be separately stored in a folder which name after the instances'`name` . 

For example, if user try to download `~/foo.txt` simultaneously from `node1` and `node2`, and designate `./bar/foo.txt` as the host file path, then `eh-vagrant ` will automatically modify the host file path, copy `~/foo.txt` on `node1` into `./bar/node1/foo.txt` and copy `~foo.txt`on `node2` into `./bar/node2/foo.txt`.

### Execute arbitrary shell command or script on instances

#### start a ssh session

Usage: ```python vagrant.py vagrant ssh NAME```

Launch a secure-shell session which connects to the vagrant instance specified by ```NAME```.

#### run arbitrary shell command

```pvagrant.py vagrant run command COMMAND [--vms=<vmList>]```

Run an arbitrary shell `COMMAND` on instances. If user specify multiple instances to run, the command will run on those instances simultaneously, i.e., in a parallel fashion.  Any output produced to the `stdout` and `stderr` of executing instances will be fetched and reformatted to a job report. Finally, the job report will print out to the current terminal.

![run_command_example](/img/run_command.png)

#### run arbitrary shell script

Usage: ```python vagrant.py vagrant run script SCRIPT [--data=PATH] [--vms=<vmList>]```

Run an arbitrary **shell script** on instances. The behavior of this command will comply with  `run command`, plus extra features defined as following:

- positional argument `SCRIPT` is the path of the script file to be executed, which must locates on the host machine. It will be uploaded and stored at the `JOB_FOLDER` of all executing instances, which locates at` ~/cm_experiment/{script_name}_{epoch_second}/`.
- If there is any data that must be run against the script, specify the path of the data (be file or folder) with `--data` argument. If `--data` is a folder, **then its' path must be end with '/'**. The data will be copied into `$JOB_FOLDER$/data/` directory of all executing instances.
- About the script and its execution:
  - If the script will ever produce any output file, it should be stored at `$JOB_FOLDER$/output/` directory. The behavior including building the `$JOB_FOLDER$/output/` folder and storing result file to that folder **should be handle by the script itself**.
  - When execution, the script will always receive the value of  `JOB_FOLDER` as its first argument. This value can be used in various ways. For example, to build the `$JOB_FOLDER$/output/` folder.

- After execution, if there exist anything in ` $JOB_FOLDER$/output/`, then it will all be fetched and stored to `./experiment/{instnace_name}/{script_name}_{epoch_second}/output/` folder on the host machine.
  - If using with `cloudmesh`, output content will be stored at `$CLOUDMESH_ROOT_DIRECTORY$/experiment/{instnace_name}/{script_name}_{epoch_second}/output/`. 

![run_script_example](/img/run_script.png)