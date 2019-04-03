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
from __future__ import print_function
from setuptools import setup, find_packages

import os
import platform
import sys


__version__ = None  # suppress the version error
# don't use import to get the version as that causes a circular dependency
exec(open('cloudmesh/cm4/__init__.py').read().strip())

v = sys.version_info
if v.major != 3 and v.minor != 7 and v.micro < 2:
    print(70 * "#")
    print("WARNING: upgrade to a python greater or eaqual to 3.7.2 "
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
apache-libcloud
certifi
chardet
colorama
config
coverage
docopt
idna
oyaml
pymongo
python-hostlist
PyYAML
requests
termcolor
urllib3
Flask-PyMongo
flask
six
recommonmark
dateparser
humanize
psutil
connexion[swagger-ui]
yamllint
azure
docker
munch
""".split("\n")


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


home = os.path.expanduser("~")

# data_files= [
#    (os.path.join(home, '.cloudmesh'),
#    [os.path.join(d, f) for f in files]) for d, folders, files in os.walk(
#                os.path.join('cloudmesh_cm4', 'etc'))]
#
# print ("DDDD", data_files)

# package_data={
#   'cloudmesh_cm4.etc': ['*.yaml', '*.py'],
# },


setup(
    version=__version__,
    name="cloudmesh-cm4",
    description="cloudmesh_cm4 - A heterogeneous multi cloud command "
                "client and shell",
    long_description=read('README.md'),
    license="Apache License, Version 2.0",
    author="Gregor von Laszewski, cloudmesh.org",
    author_email="laszewski@gmail.com",
    url="https://github.com/cloudmesh-community/cm",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Windows :: 10",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Clustering",
        "Topic :: System :: Distributed Computing",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Console"
    ],
    keywords="cloud cmd commandshell plugins",
    packages=find_packages(),
    install_requires=requiers,
    namespace_packages=['cloudmesh'],
    include_package_data=True,
    # data_files= data_files,
    package_data={
        'cm4.etc': ['*.yaml', '*.py'],
    },
    #entry_points={
    #    'console_scripts': [
    #        'cm4 = cm4.command.command:main',
    #    ],
    #},
    # tests_require=['tox'],
    # dependency_links = []
)
