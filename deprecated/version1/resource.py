#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 23 18:07:10 2018

@author: yuluo
"""
import sys
import yaml


class Resource(object):

    def __init__(self, debug=False):
        """
        initializes the resource class for awscm

        :param debug: enables debug information to be printed
        """

        self.yamlFile = "/Users/yuluo/Desktop/cloudmesh.yaml"
        self.debug = debug

    def readFile(self, yamlFile):
        """
        read the default yaml file
        :param yamlFile: the target yaml file
        :return cloudmesh: the content of the yaml file
        """

        cloudmesh = ""
        with open(yamlFile, "r") as stream:
            try:
                cloudmesh = yaml.load(stream, Loader=yaml.FullLoader)
            except yaml.YAMLError as exc:
                print(exc)
        return cloudmesh

    def updateFile(self, newContent):
        """
        update the new content into the default yaml file
        :param newContent: the new content
        """

        with open(self.yamlFile, "w") as output:
            yaml.dump(newContent, output)

    def add(self, content, filePath):
        """
        reand the content from a yaml file, and add it into the default yaml file

        :param content: the default yaml file
        :param filePath: the new content file location
        """

        newContent = self.readFile(filePath)
        for i in newContent:
            (((content["cloudmesh"])['cloud'])['test']).update({i: newContent[i]})
        self.updateFile(content)

    def remove(self, content, item):
        """
        remove the labeled or named content from the default yaml file

        :param content: the default yaml content
        :param item: the label or name of the instance that would be removed
        """

        for i in ((content['cloudmesh'])['cloud'])['test']:
            if ((((content['cloudmesh'])['cloud'])['test'])[i])['name'] == item or \
                    ((((content['cloudmesh'])['cloud'])['test'])[i])['label'] == item:
                del (((content['cloudmesh'])['cloud'])['test'])[i]
                break
        self.updateFile(content)

    def review(self, item, cloud, cluster, default):
        """
        review named or labeled instance from default yaml file

        :param item: label or name of the instance we want to review
        :param cloud: the cloud block of the default yaml file
        :param cluster: the cluster block of the default yaml file
        :param default: the default block of the default yaml file
        :return result: the content of the named or labeled instance in yaml file
        """

        result = {}
        for i in cloud:
            for j in cloud[i]:
                if ((cloud[i])[j])['name'] == item or ((cloud[i])[j])['label'] == item:
                    result = {j: (cloud[i])[j]}
        for i in cluster:
            if (cluster[i])['name'] == item or (cluster[i])['label'] == item:
                result = {i: cluster[i]}

        if result == {}:
            print('Cannot find the instance ' + item + ', please check the instance label or name')
            sys.exit()
        else:
            return result
