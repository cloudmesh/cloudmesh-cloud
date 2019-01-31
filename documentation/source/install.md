# Installation

## Prerequisites

Before you install make sure that you have at minimum python 3.7.1 
installed. We
recommend that you use a python virtualenv such as venv or pyenv to
isolate the python installed packages as not to interfere with the
system installation.

## Anaconda and Conda

At this time we do not yet support conda. But if you like to 
contribute an instalation package, please do so.
 
It may just very well work with our pip installs, but we have not tested it. 
Please give us feedback.

### Source instalation for development

For now you must use the source instalation as all other instalations 
will not yet work


```bash
export SRC=~/github
mkdir $SRC
cd $SRC
git clone https://github.com/cloudmesh/cloudmesh.common.git
git clone https://github.com/cloudmesh/cloudmesh.cmd5.git
git clone https://github.com/cloudmesh/cloudmesh.sys.git
git clone https://github.com/cloudmesh-community/cloudmesh.cm.git

cd $SRC/cloudmesh.common
python setup.py install
pip install -r requirements.txt
pip install -e .
cd $SRC/cloudmesh.cmd5
pip install -r requirements.txt
python setup.py install
pip install -e .
cd $SRC/cloudmesh.sys
pip install -r requirements.txt
python setup.py install
pip install -e .
cd $SRC/cm
pip install -r requirements.txt
python setup.py install
pip install -e .
```

## One Line installer

:warning: Does not work yet

```bash
wget -qO - http://cloudmesh.github.io/get/cm4/osx | sh 
```


## Installation of mongod

BUG: Install on windows is not yet implemented or tested

In case your computer does not yet have mongo db installed, you can
easily install it with our `admin` command. It will not only install
mongo, but also add the path to your .bash_* file. To install it
simply say

```bash
$ cms admin mongo install
```

It will download and install the version we use.

