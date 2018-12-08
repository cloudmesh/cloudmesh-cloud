from docopt import docopt

import cm4
from cloudmesh.common.dotdict import dotdict
from pprint import pprint
from cloudmesh.common.Printer import Printer
from cloudmesh.common.Shell import Shell
import sys
import os
from cm4 import __version__
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
import cm4.vbox
from cm4.vbox.search import search

# from cm4.mongo.MongoDBController import MongoDBController
# from cm4.mongo.MongoDBController import MongoInstaller



# pprint (vbox.vm.list())
# vbox.vm.execute("w2", "uname")
# pprint (vbox.image.list())

#
# TODO: revisit Printer

def defaults():
    """
    default values
    :return: a number of default values for memory, image, and script
    :rtype: dotdict
    """
    # TODO, read this from yaml file
    d = dotdict()
    d.memory = 1024
    # d.image = "ubuntu/xenial64"
    d.image = "ubuntu/trusty64"
    d.port = 8080
    d.script = None
    return d


#
# TODO: this seems generally useful, we may want to put this in common
#
def _convert(lst, id="name"):
    d = {}
    for entry in lst:
        d[entry[id]] = entry
    return d


def _LIST_PRINT(l, output, order=None):
    if output in ["yaml", "dict", "json"]:
        l = _convert(l)

    result = Printer.write(l,
                           order=order,
                           output=output)

    if output in ["table", "yaml", "json", "csv"]:
        print(result)
    else:
        pprint(result)



class VboxCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_vbox(self, args, arguments):
        """
        ::

          Usage:
            vbox version [--format=FORMAT]
            vbox image search [--url=URL]
            vbox image list [--format=FORMAT]
            vbox image find NAME
            vbox image add NAME
            vbox image search
            vbox vm list [--format=FORMAT] [-v]
            vbox vm delete NAME
            vbox vm config NAME
            vbox vm ip NAME [--all]
            vbox create NAME ([--memory=MEMORY] [--image=IMAGE] [--script=SCRIPT] | list)
            vbox vm boot NAME ([--memory=MEMORY] [--image=IMAGE] [--port=PORT] [--script=SCRIPT] | list)
            vbox vm ssh NAME [-e COMMAND]
        """

        arguments.format = arguments["--format"] or "table"
        arguments.verbose = arguments["-v"]
        arguments.all = arguments["--all"]

        print (arguments)

        if arguments.version:
            versions = {
                "vbox": {
                   "attribute": "Vagrant Version",
                    "version": cm4.vbox.version(),
                },
                "cloudmesh-vbox": {
                    "attribute":"cloudmesh vbox Version",
                    "version": __version__
                }
            }
            _LIST_PRINT(versions, arguments.format)

        elif arguments.image and arguments.list:
            l = cm4.vbox.image.list()
            _LIST_PRINT(l, arguments.format, order=["name", "provider", "date"])

        elif arguments.image and arguments.add:
            l = cm4.vbox.image.add(arguments.NAME)
            print(l)

        elif arguments.image and arguments.find:
            l = cm4.vbox.image.find(arguments.NAME)
            print(l)

        elif arguments.vm and arguments.list:
            l = cm4.vbox.vm.list()
            _LIST_PRINT(l,
                       arguments.format,
                       order=["name", "state", "id", "provider", "directory"])

        elif arguments.create and arguments.list:

            result = Shell.cat("{NAME}/Vagrantfile".format(**arguments))
            print (result)

        elif arguments.create:

            d = defaults()

            arguments.memory = arguments["--memory"] or d.memory
            arguments.image = arguments["--image"] or d.image
            arguments.script = arguments["--script"] or d.script

            cm4.vbox.vm.create(
                name=arguments.NAME,
                memory=arguments.memory,
                image=arguments.image,
                script=arguments.script)

        elif arguments.config:

            # arguments.NAME
            d = cm4.vbox.vm.info(name=arguments.NAME)

            result = Printer.attribute(d, output=arguments.format)

            print (result)

        elif arguments.ip:

            data = []
            result = cm4.vbox.vm.execute(arguments.NAME, "ifconfig")
            if result is not None:
                lines = result.splitlines()[:-1]
                for line in lines:
                    if "inet addr" in line:
                        line = line.replace("inet addr", "ip")
                        line = ' '.join(line.split())
                        _adresses = line.split(" ")
                        address = {}
                        for element in _adresses:
                            attribute, value = element.split(":")
                            address[attribute] = value
                        data.append(address)
            if arguments.all:
                d = {}
                i = 0
                for e in data:
                    d[str(i)] = e
                    i = i + 1
                result = Printer.attribute(d, output=arguments.format)
                print(result)
            else:
                for element in data:
                    ip = element['ip']
                    if  ip == "127.0.0.1" or ip.startswith("10."):
                        pass
                    else:
                        print (element['ip'])


        elif arguments.boot:

            d = defaults()

            arguments.memory = arguments["--memory"] or d.memory
            arguments.image = arguments["--image"] or d.image
            arguments.script = arguments["--script"] or d.script
            arguments.port = arguments["--port"] or d.port

            cm4.vbox.vm.boot(
                name=arguments.NAME,
                memory=arguments.memory,
                image=arguments.image,
                script=arguments.script,
                port=arguments.port)

        elif arguments.delete:

            result = cm4.vbox.vm.delete(name=arguments.NAME)
            print(result)

        elif arguments.ssh:

            if arguments.COMMAND is None:
                os.system("cd {NAME}; vbox ssh {NAME}".format(**arguments))
            else:
                result = cm4.vbox.vm.execute(arguments.NAME, arguments.COMMAND)
                if result is not None:
                    lines = result.splitlines()[:-1]
                    for line in lines:
                        print (line)

        else:

            print ("use help")

        result = ""
        return result