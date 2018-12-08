from cloudmesh.common.Shell import Shell
from cloudmesh.common.dotdict import dotdict
import textwrap
import os
from cloudmesh.common.console import Console
from pprint import pprint


class vm(object):
    @classmethod


    @classmethod


    @classmethod
    def info(cls, name=None):
        result = Shell.execute("vagrant",
                               ["ssh-config"],
                               cwd=name)
        lines = result.split("\n")
        data = {}
        for line in lines:
            attribute, value = line.strip().split(" ", 1)
            if attribute == "IdentityFile":
                value = value.replace('"','')

            data[attribute] = value
        return data





    @classmethod
    def boot(cls, **kwargs):

        arg = dotdict(kwargs)
        arg.cwd = kwargs.get("cwd", None)

        vms = cls.to_dict(cls.list())

        if arg.name in vms:
            Console.error("vm {name} already booted".format(**arg), traceflag=False)
            return None
        # print result

        else:
            cls.create(**kwargs)
            Console.ok("{name} created".format(**arg))
            Console.ok("{name} booting ...".format(**arg))

            result = Shell.execute("vagrant",
                                   ["up", arg.name],
                                   cwd=arg.name)
            Console.ok("{name} ok.".format(**arg))

            return result


    @classmethod
    def execute(cls, name, command, cwd=None):

        vms = cls.to_dict(cls.list())

        arg = "ssh {} -c {}".format(name, command)
        result = Shell.execute("vagrant", ["ssh", name, "-c", command], cwd=vms[name]["directory"])
        return result

    # TODO: Seems replicated
    @classmethod
    def to_dict(cls, lst, id="name"):
        d = {}
        for entry in lst:
            d[entry[id]] = entry
        return d
