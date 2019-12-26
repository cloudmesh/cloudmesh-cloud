#!/usr/bin/env python
# ----------------------------------------------------------------------- #
# Copyright 2008-2010, Gregor von Laszewski                               #
# Copyright 2010-2018, cloudmesh.org                                      #
#                                                                         #
# Licensed under the Apache License, Version 2.0 (the "License"); you may #
# not use this file except in compliance with the License. You may obtain #
# a copy of the License at                                                #
#                                                                         #
# http://www.apache.org/licenses/LICENSE-2.0                              #
#                                                                         #
# Unless required by applicable law or agreed to in writing, software     #
# distributed under the License is distributed on an "AS IS" BASIS,       #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.#
# See the License for the specific language governing permissions and     #
# limitations under the License.                                          #
# ------------------------------------------------------------------------#
from setuptools import setup, find_packages

import os
import platform
import sys
import io

from setuptools import find_packages, setup


v = sys.version_info
if v.major != 3 and v.minor != 7 and v.micro < 2:
    print(70 * "#")
    print("WARNING: upgrade to a python greater or equal to 3.7.3 "
          "other version may not be  supported. "
          "Your version is {version}. ".format(version=sys.version_info))
    print(70 * "#")

command = None
this_platform = platform.system().lower()
#if this_platform in ['darwin']:
#    command = "easy_install readline"
#elif this_platform in ['windows']:
#    command = "pip install pyreadline"
#if command is not None:
#    print("Install readline")
#    os.system(command)

requiers = """
cloudmesh-configuration
cloudmesh-cmd5
cloudmesh-sys
cloudmesh-inventory
apache-libcloud
azure
beautifulsoup4
boto3
certifi
chardet
colorama
config
connexion[swagger-ui]
coverage
cryptography
dateparser
docker
docopt
flask
Flask-PyMongo
humanize
idna
munch
openstacksdk
oyaml
pandas
progress
psutil
pymongo
python-hostlist
PyYAML
recommonmark
requests
selenium
tabulate
termcolor
urllib3
uuid
yamllint
""".split("\n")


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

with open('README.md') as f:
    long_description = f.read()

NAME = "cloudmesh-cloud"
DESCRIPTION = "Cloudmesh Multicloud Cloud Plugins for Cloudmesh cmd5 CMD"
AUTHOR = "Gregor von Laszewski"
AUTHOR_EMAIL = "laszewski@gmail.com"
URL = "https://github.com/cloudmesh/cloudmesh-cloud"


setup(
    name=NAME,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="4.3.0",
    license="Apache 2.0",
    url=URL,
    packages=find_packages(exclude=("tests",
                                    "deprecated",
                                    "propose",
                                    "examples",
                                    "conda")),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: MacOS X",
        "Environment :: OpenStack",
        "Environment :: Other Environment",
        "Environment :: Plugins",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: System",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Shells",
        "Topic :: Utilities",
    ],
    install_requires=requiers,
    tests_require=[
        "flake8",
        "coverage",
    ],
    zip_safe=False,
    namespace_packages=['cloudmesh'],
)
