# Instalation

## Prerequisits

Before you install make sure that you have python 3.7.1 installed. We recommedn that you use a pythin virtualenv such as venv or pyenv to isolate the python installed packages as not to interfere with the system instalation

We do at this time not have a conda package

## Instalation of Cloudmesh 4

Cloudmesh 4 can be installed from pip, or from source. For now we recommend the source instalation

```bash
$ git clone https://github.com/cloudmesh-community/cm.git
$ cd cm
$ pip install -r requirements.txt
$ pip install .
```

## Instalation of mongod

In case your computer does not yet have mongo db installed, you acn easily install it with our `admin` command. It will not only install mongo, but also add the path to your .bash_* file. To install it simply say

```bash
$ cm4 admin mongo install
```

It will download and install the version we use.

BUG: Install on windows is not yet implemented
