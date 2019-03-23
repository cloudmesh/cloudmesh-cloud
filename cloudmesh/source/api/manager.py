import os
from pprint import pprint
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.util import path_expand
from cloudmesh.common.console import Console


class Manager(object):

    def __init__(self, config, protocol="ssh"):

        self.config = config
        self.data = {}

        for software in config:

            self.data[software] = source = dotdict(
                {
                    "software": software,
                    "directory": path_expand(config[software]),

                }
            )
            if software in ["cm"]:
                source["community"] = "cloudmesh-community"
                source["preface"] = ""
            else:
                source["community"] = "cloudmesh"
                source["preface"] = "cloudmesh."

            source["path"] = os.path.join(config[software],
                                          source["preface"] + software)

            if format == "ssh":
                source[
                    "git"] = "git@github.com:{community}/{preface}{software}.git".format(
                    **dict(source))
            else:
                source[
                    "git"] = "https://github.com/{community}/{preface}{software}.git".format(
                    **dict(source))

    def install(self):

        for software in self.config:
            source = self.data[software]
            if not os.path.exists(source["path"]):
                source["command"] = "cd {path}; git pull".format(**dict(source))
            else:
                source[
                    "command"] = "cd {directory}; git clone {software}".format(
                    **dict(source))

        pprint(self.data)
        for software in self.config:
            command = path_expand(self.data[software]['command'])
            Console.ok(command)
            os.system(command)

    def update(self):
        print("update", self.config)

    def dict(self):
        return self.data
