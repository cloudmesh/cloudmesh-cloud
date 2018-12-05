#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 23:57:04 2018

@author: yuluo
"""

from deprecated.ResourceABC import ResourceABC
import oyaml as yaml
import os


class Resource(ResourceABC):

    def __init__(self):
        # TODO:
        self.yamlFile = os.path.expanduser("~/.cloudmesh/cloudmesh.yaml")

    def readFile(self, yaml_file):
        cloudmesh = ""
        with open(yaml_file, "r") as stream:
            try:
                cloudmesh = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        return cloudmesh

    def add(self, content, file_path):
        new_content = self.readFile(file_path)
        for i in new_content:
            ((content["cloudmesh"])["cluster"]).update({i: new_content[i]})
        self.updateFile(content)

    def listAll(self, content):
        computer = yaml.dump((content["cloudmesh"])["cluster"])
        print(computer)

    def remove(self, content, file_path):
        new_content = self.readFile(file_path)
        for i in new_content:
            del ((content["cloudmesh"])["cluster"])[i]
        self.updateFile(content)

    def updateFile(self, new_content):
        with open(self.yamlFile, "w") as output:
            yaml.dump(new_content, output)
