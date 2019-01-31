# Installation

## One Line installer

Does not work yet 

```bash
wget -qO - http://cloudmesh.github.io/get/cm4/osx | sh 
```


## Prerequisites

Before you install make sure that you have at minimum python 3.7.1 installed. We
recommend that you use a python virtualenv such as venv or pyenv to
isolate the python installed packages as not to interfere with the
system installation.

We do at this time not have a conda package or have tested it on conda.

## Installation of Cloudmesh 4

Cloudmesh 4 can be installed from pip, or from source. For now we
recommend the source installation

.. note: the pip instalation is not yet working

```bash
$ git clone https://github.com/cloudmesh-community/cm.git
$ cd cm
$ pip install -r requirements.txt
$ pip install .
```

## Installation of mongod

In case your computer does not yet have mongo db installed, you can
easily install it with our `admin` command. It will not only install
mongo, but also add the path to your .bash_* file. To install it
simply say

```bash
$ cms admin mongo install
```

It will download and install the version we use.

BUG: Install on windows is not yet implemented
