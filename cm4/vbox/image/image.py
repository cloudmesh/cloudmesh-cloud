from cloudmesh.common.Shell import Shell
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.console import Console
import os
import webbrowser


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
        d = {
            'key': name,
            'location': "https://app.vagrantup.com/boxes/search"
        }
        # cls.search(u"https://app.hashicorp.com/boxes/search?utf8=\&sort=\&provider=\&q={key}".format(**d))

        link="{location}?utf8=%E2%9C%93&sort=downloads&provider=&q=\"{key}\"".format(**d)
        webbrowser.open(link, new=2, autoraise=True)
