# Installation

## Prerequisites

Before you install make sure that you have at minimum python 3.7.2 installed. We
recommend that you use a python virtualenv such as venv or pyenv to isolate the
python installed packages as not to interfere with the system installation.


### Source instalation for development

For now you must use the source instalation as all other instalations 
will not yet work


```bash
export SRC=`pwd`
git clone https://github.com/cloudmesh/cloudmesh.common.git
git clone https://github.com/cloudmesh/cloudmesh.cmd5.git
git clone https://github.com/cloudmesh/cloudmesh.sys.git
git clone https://github.com/cloudmesh-community/cm.git

cd $SRC/cloudmesh.common
pip install -e .
cd $SRC/cloudmesh.cmd5
pip install -e .
cd $SRC/cloudmesh.sys
pip install -e .
cd $SRC/cm
pip install -e .
```

## Installation of mongod

First, you will need to install a `cloudmesh4.yaml` file, if you have not done 
this before. The easieast wy to do so is with the command

```bash
$ cms help
```
 
Now you will need to edit the file

`~/.cloudmesh/cloudmesh4.yaml`

and change the password of the mongo entry to something you like, e.g. change
 the TBD to a real strong password

```
      MONGO_PASSWORD: TBD
```

In case you do not have mongod installed, you can do so for macOS and Ubuntu 
18.xx by setting the following variable:

```
      MONGO_AUTOINSTALL: True
```


Now you can run the `admin mongo install` command. It will not only install
mongo, but also add the path to your `.bash_*` file. To install it simply say

```bash
$ cms admin mongo install
```

To create a password protection you than run the command

```bash
$ cms admin mongo create
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

At this time we do not yet support conda. But if you like to contribute an
instalation package, please do so.
 
It may just very well work with our pip installs, but we have not tested it. 
Please give us feedback.
