from cloudmesh_client.common.Shell import Shell
from cloudmesh_client.common.dotdict import dotdict
from cloudmesh_client.shell.console import Console
import os

class image(object):
    @classmethod
    def list(cls):
        def convert(line):
            line = line.replace("(", "")
            line = line.replace(")", "")
            line = line.replace(",", "")
            entry = line.split(" ")
            data = dotdict()
            data.name = entry[0]
            data.provider = entry[1]
            data.date = entry[2]
            return data

        result = Shell.execute("vagrant", ["box", "list"])

        lines = []
        for line in result.split("\n"):
            lines.append(convert(line))
        return lines

    @classmethod
    def add(cls, name):

        result = Shell.execute("vagrant", ["box", "add", name])
        return result

    @classmethod
    def find(cls, name):
        Console.error("not yet implemented")
        d = {'key': name}
        os.system (u"open " + u"https://atlas.hashicorp.com/boxes/search?utf8=\&sort=\&provider=\&q={key}".format(**d))