# Installation

## Prerequisites

Before you install make sure that you have at minimum python 3.7.2
installed. We recommend that you use a python virtualenv such as `venv`
or `pyenv` to isolate the python installed packages as not to interfere
with the system installation.

### Installation via pip development

The installation via pip is not yet supported for cloudmesh cm. Thus
we recommend that you use the source installation instead.

In future cloudmesh version 4 will be installed with

```bash
pip install cloudmesh.cm
```

Individual packages can be installed with

```
pip install cloudmesh.common
pip install cloudmesh.sys
pip install cloudmesh.cmd5
pip install cloudmesh.openapi
```

For the time being we recommend you conduct the source install.

### Source installation for development

For developers we recommend the source installation as all other installations
will not yet work


```bash
export SRC=`pwd`
git clone https://github.com/cloudmesh/cloudmesh.common.git
git clone https://github.com/cloudmesh/cloudmesh.cmd5.git
git clone https://github.com/cloudmesh/cloudmesh.sys.git
git clone https://github.com/cloudmesh/cloudmesh.openapi.git
git clone https://github.com/cloudmesh-community/cm.git


cd $SRC/cloudmesh.common
pip install -e .
cd $SRC/cloudmesh.cmd5
pip install -e .
cd $SRC/cloudmesh.sys
pip install -e .
cd $SRC/cloudmesh.openapi
pip install -e .
cd $SRC/cm
pip install -e .
```

## Installation of mongod

First, you will need to install a `cloudmesh4.yaml` file, if you have
not done this before. The easieast wy to do so is with the command

```bash
$ cms help
```
 
Now you will need to edit the file

`~/.cloudmesh/cloudmesh4.yaml`

and change the password of the mongo entry to something you like,
 e.g. change the TBD to a real strong password

```
      MONGO_PASSWORD: TBD
```

In case you do not have mongod installed, you can do so for macOS and Ubuntu 
18.xx by setting the following variable:

```
      MONGO_AUTOINSTALL: True
```


Now you can run the `admin mongo install` command. It will not only
install mongo, but also add the path to your `.bash_*` file. In case
of windows platform, you will have to set the PATH variable
manually. To install it simply say.

```bash
$ cms admin mongo install
```

To create a password protection you than run the command

```bash $ cms admin mongo create ``` Incase of Windows platform, after
executing above command, open a new cms session and execute below
commands.

```bash
$ cms admin mongo start
```

Once the mongo db is created it and be started and stoped with 

```bash
$ cms admin mongo start
$ cms admin mongo stop
```

For cloudmesh to work properly, please start mongo.

## One Line installer (proposed)

:warning: Does not work yet

```bash
wget -qO - http://cloudmesh.github.io/get/cm4/osx | sh 
```

## Anaconda and Conda (proposed)

At this time we do not yet support conda. But if you like to
contribute an instalation package, please do so.
 
It may just very well work with our pip installs, but we have not
tested it.  Please give us feedback.
