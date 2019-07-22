import os
from pprint import pprint

from cloudmesh.cloud import __version__
from cloudmesh.common.Printer import Printer
from cloudmesh.common.Shell import Shell
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.dotdict import dotdict
from cloudmesh.compute.virtualbox.Provider import Provider
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command


# from cloud.mongo.MongoDBController import MongoDBController
# from cloud.mongo.MongoDBController import MongoInstaller


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


# noinspection PyPep8Naming
def _LIST_PRINT(l, output, order=None):
    if output in ["yaml", "dict", "json"]:
        l_converted = _convert(l)
    else:
        l_converted = l

    result = Printer.write(l_converted,
                           order=order,
                           output=output)

    if output in ["table", "yaml", "json", "csv"]:
        print(result)
    else:
        pprint(result)


class VboxCommand(PluginCommand):

    # noinspection PyUnusedLocal,PyPep8
    @command
    def do_vbox(self, args, arguments):
        """
        ::

          Usage:
            vbox version [--output=OUTPUT]
            vbox image list [--output=OUTPUT]
            vbox image find KEYWORDS...
            vbox image add NAME
            vbox image delete NAME
            vbox vm info NAME
            vbox vm list [--output=OUTPUT] [-v]
            vbox vm delete NAME
            vbox vm ip [NAME] [--all]
            vbox vm create [NAME] ([--memory=MEMORY] [--image=IMAGE] [--port=PORT] [--script=SCRIPT]  | list)
            vbox vm boot [NAME] ([--memory=MEMORY] [--image=IMAGE] [--port=PORT] [--script=SCRIPT] | list)
            vbox vm ssh [NAME] [-e COMMAND]
        """

        arguments.output = arguments["--output"] or "table"
        arguments.verbose = arguments["-v"]
        arguments.all = arguments["--all"]

        #
        # ok
        #
        def list_images():
            images = Provider().images()
            _LIST_PRINT(images, arguments.output,
                        order=["name", "provider", "version"])

        #
        # ok
        #
        # noinspection PyShadowingNames
        def image_command(func):
            try:
                images = func(arguments.NAME)
                print(images)
                images()
            except Exception as e:
                print(e)
            return ""

        #
        # ok
        #
        if arguments.version:
            p = Provider()

            versions = {
                "cm": {
                    "attribute": "cm",
                    "description": "Cloudmesh vbox Version",
                    "version": __version__
                },
                "vbox": {
                    "attribute": "vbox",
                    "description": "Vagrant Version",
                    "version": p.version()
                }
            }
            result = Printer.write(versions,
                                   order=["attribute", "version",
                                          "description"],
                                   output=arguments.output)
            print(result)

        #
        # ok
        #
        elif arguments.image and arguments.list:
            list_images()
        #
        # ok
        #
        elif arguments.image and arguments.delete:
            image_command(Provider().delete_image)
        #
        # ok
        #
        elif arguments.image and arguments.put:
            image_command(Provider().add_image)

        #
        # ok
        #
        elif arguments.image and arguments.find:
            Provider().find_image(arguments.KEYWORDS)
            return ""

        #
        # ok, but only vagrant details
        #
        elif arguments.vm and arguments.list:

            provider = Provider().vagrant_nodes()
            _LIST_PRINT(provider,
                        arguments.output,
                        order=["name", "state", "id", "provider", "directory"])
            return ""

        #
        # unclear: this function is unclear
        #
        elif arguments.create and arguments.list:

            result = Shell.cat("{NAME}/Vagrantfile".format(**arguments))
            if result is not None:
                print(result)
            return ""

        elif arguments.create:

            d = defaults()

            VERBOSE(d)

            arguments.memory = arguments["--memory"] or d.memory
            arguments.image = arguments["--image"] or d.image
            arguments.script = arguments["--script"] or d.script
            arguments.port = arguments["--port"] or d.port

            server = Provider()
            server.create(**arguments)

        elif arguments.info:

            # arguments.NAME
            d = Provider().info(name=arguments.NAME)

            result = Printer.write(d, output=arguments.output)

            print(result)

        elif arguments.ip:

            data = []
            result = Provider().execute(arguments.NAME, "ifconfig")
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
                result = Printer.attribute(d, output=arguments.output)
                print(result)
            else:
                for element in data:
                    ip = element['ip']
                    if ip == "127.0.0.1" or ip.startswith("10."):
                        pass
                    else:
                        print(element['ip'])

        elif arguments.boot:

            d = defaults()

            pprint(d)

            arguments.memory = arguments["--memory"] or d.memory
            arguments.image = arguments["--image"] or d.image
            arguments.script = arguments["--script"] or d.script
            arguments.port = arguments["--port"] or d.port

            node = Provider().boot(
                name=arguments.NAME,
                memory=arguments.memory,
                image=arguments.image,
                script=arguments.script,
                port=arguments.port)

        elif arguments.delete:

            result = Provider().delete(name=arguments.NAME)
            print(result)

        elif arguments.ssh:

            if arguments.COMMAND is None:
                os.system("cd {NAME}; vbox ssh {NAME}".format(**arguments))
            else:
                result = Provider().execute(arguments.NAME, arguments.COMMAND)
                if result is not None:
                    lines = result.splitlines()[:-1]
                    for line in lines:
                        print(line)

        else:

            print("use help")

        result = ""
        return result
