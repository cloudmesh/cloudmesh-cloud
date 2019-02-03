# -*- coding: utf-8 -*-
"""
We use a uniform naming convention method. The name is defined by different kinds of
objects.

a name has the following hierarchy

experiment
  group
    user
      kind
        counter

However the counter is always increasing

Experiment: is an experiment that all cloud objects can be placed under.

Group: A group formulates a number of objects that logically build an entity,
such as a number of virtual machines building a cluster

User: A user name that may control the grou

Kind: A kind that identifies whit cind of resource this is

"""
import re
from cloudmesh.management.configuration.counter import Counter
from cloudmesh.common.dotdict import dotdict
from pprint import pprint
from cloudmesh.db.strdb import YamlDB
from cloudmesh.common.util import path_expand
import os
import yaml

class Name(dotdict):

    def __init__(self, order=["experiment","group","user","kind","counter"], **kwargs):
        """
        Defines a name tag that sets the format of the name to the specified schema
        :param schema:
        """
        if "path" not in kwargs:
            self.__dict__['path'] = path_expand("~/.cloudmesh/name.yaml")
        prefix = os.path.dirname(self.__dict__['path'])
        if not os.path.exists(prefix):
            os.makedirs(prefix)

        if os.path.exists(self.path):
            with open(self.path, 'rb') as dbfile:
                self.__dict__ = yaml.safe_load(dbfile) or dict()

        self.__dict__['order'] = order
        self.__dict__['schema'] = "{" + "}-{".join(order) + "}"
        for name in kwargs:
            self.__dict__[name] = kwargs[name]
        #self.data = kwargs

    def flush(self):
        string = yaml.dump(self.__dict__, default_flow_style=False)
        bits = bytes(string, encoding='utf-8')
        with open(self.path, 'wb') as dbfile:
            dbfile.write(bits)

    def incr(self):
        self.__dict__["counter"] += 1
        self.flush()

    def reset(self):
        self.__dict__["counter"] = 1
        self.flush()

    def get(self, kind):
        """
        overwrites the kind
        :param kind: The kind
        :return: the string representation
        """
        self.__dict__["kind"] = kind
        return self.__str__()


    def __str__(self):
        return str(self.__dict__["schema"].format(**self.__dict__))


    def dict(self):
        return self.__dict__

# Make a unit test

# %% usage/test
# a={'experiment':'a',
#    'group':'b',
#    'user':'gregor',
#    'counter':0}
# name=Name(a)
#
# print(name.get(a))
# print(name.get())
