from __future__ import print_function

import textwrap

from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.dotdict import dotdict
from cloudmesh.management.configuration.config import Config
from cloudmesh.management.configuration.operatingsystem import OperatingSystem
# from cloudmesh.admin.api.manager import Manager
from cloudmesh.mongo.MongoDBController import MongoDBController
from cloudmesh.mongo.MongoDBController import MongoInstaller
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand


class AdminCommand(PluginCommand):
    banner = textwrap.dedent("""
        test
        +-------------------------------------------------------+
        |   ____ _                 _                     _      |
        |  / ___| | ___  _   _  __| |_ __ ___   ___  ___| |__   |
        | | |   | |/ _ \| | | |/ _` | '_ ` _ \ / _ \/ __| '_ \  |
        | | |___| | (_) | |_| | (_| | | | | | |  __/\__ \ | | | |
        |  \____|_|\___/ \__,_|\__,_|_| |_| |_|\___||___/_| |_| |
        +-------------------------------------------------------+
        |                  Cloudmesh CMD5 Shell                 |
        +-------------------------------------------------------+
        """)

    # noinspection PyUnusedLocal
    @command
    def do_admin(self, args, arguments):
        """
        ::

          Usage:
            admin mongo install [--brew] [--download=PATH]
            admin mongo create
            admin mongo status
            admin mongo stats
            admin mongo version
            admin mongo start
            admin mongo stop
            admin mongo backup FILENAME
            admin mongo load FILENAME
            admin mongo security
            admin mongo password PASSWORD
            admin mongo list
            admin rest status
            admin rest start
            admin rest stop
            admin status
            admin system info
            admin yaml cat
            admin yaml check

          The admin command performs some administrative functions, such as installing packages, software and services.
          It also is used to start services and configure them.

          Arguments:
            FILENAME  the filename for backups

          Options:
            -f      specify the file

          Description:

            Mongo DB

              MongoDB is managed through a number of commands.

              The configuration is read from ~/.cloudmesh/cloudmesh4.yaml

              First, you need to create a MongoDB database with

                cms admin mongo create

              Second, you need to start it with

                 cms admin mongo start

              Now you can interact with it to find out the status, the stats,
              and the database listing with the commands

                 cms admin mongo status
                 cms admin mongo stats
                 cms admin mongo list

              To stop it from running use the command

                 cms admin mongo stop

              System information about your machine can be returned by

                 cms admin system info

              This can be very useful in case you are filing an issue or bug.
        """

        # arguments.PATH = arguments['--download'] or None
        result = None

        if arguments.mongo:

            if arguments.install:

                print("MongoDB install")
                print(79 * "=")
                installer = MongoInstaller()
                r = installer.install()
                return r

            elif arguments.status:

                mongo = MongoDBController()
                state = mongo.status()

                if "error" in state["status"]:
                    Console.error(state["message"])
                    print(Printer.attribute(state))
                else:
                    data = dotdict()

                    for pid in state['output']:
                        entry = state['output'][pid]
                        data["pid"] = state['output'][pid]
                        data["command"] = state['output'][pid]['command'].strip()

                    print(Printer.dict(data, order=["pid", "command"]))
                    Console.ok(str(data.pid['pid']) + " " + state["message"])

            elif arguments.version:
                print("MongoDB Version")
                print(79 * "=")
                mongo = MongoDBController()
                r = mongo.version()
                print(r)

            elif arguments.security:

                mongo = MongoDBController()
                mongo.set_auth()
                print()

            elif arguments.create:

                print("MongoDB create")
                MongoDBController().create()

            elif arguments.start:

                print("MongoDB start")
                MongoDBController().start(security=True)

            elif arguments.stop:

                print("MongoDB stop")
                MongoDBController().stop()

            elif arguments.backup:

                print("MongoDB backup")
                MongoDBController().dump(arguments.get('FILENAME'))

            elif arguments.load:

                print("MongoDB backup")
                MongoDBController().restore(arguments.get('FILENAME'))

            elif arguments.stats:

                mongo = MongoDBController()
                r = mongo.stats()

                if len(r) > 0:
                    print(Printer.attribute(r))
                    Console.ok("ok")
                else:
                    Console.ok("is your MongoDB server running")

            elif arguments.list:

                mongo = MongoDBController()
                r = mongo.list()

                if len(r) > 0:
                    print(Printer.dict(r, order=["name", "sizeOnDisk", "empty"]))
                    Console.ok("ok")
                else:
                    Console.ok("is your MongoDB server running")

        elif arguments.yaml and arguments.cat:

            path = path_expand("~/.cloudmesh/cloudmesh4.yaml")

            secrets = [
                "AZURE_SUBSCRIPTION_ID",
                "AZURE_TENANTID",
                "EC2_ACCESS_ID",
                "EC2_SECRET_KEY",
                "OS_PASSWORD",
                "MONGO_PASSWORD"
            ]

            with open(path) as f:
                content = f.read().split("\n")

            for line in content:
                if "TBD" not in line:
                    for attribute in secrets:
                        if attribute + ":" in line:
                            line = line.split(":")[0] + ": ********"
                            break
                print(line)
            return ""

        elif arguments.yaml and arguments.check:

            path = path_expand("~/.cloudmesh/cloudmesh4.yaml")
            print()
            r = Shell.live('/Users/grey/.pyenv/shims/yamllint ' + path)
            print(70 * '-')
            print(" line:column  description")
            print()

        elif arguments.rest:

            if arguments.start:

                print("Rest Service start")
                raise NotImplementedError

            elif arguments.stop:

                print("Rest Service stop")
                raise NotImplementedError

            elif arguments.status:

                print("Rest Service status")
                raise NotImplementedError

        elif arguments.status:

            config = Config()
            data = config.data["cloudmesh"]["data"]["mongo"]
            # self.expanduser()

            print("Rest Service status")

            print("MongoDB status")

            mongo = MongoDBController()

            print(mongo)
            # mongo.expanduser()
            # data = mongo.data
            # print ("DDD", data)

            # data["MONGO_VERSION"]  = '.'.join(str(x) for x in mongo.version())

            # print (data)
            # print(Printer.attribute(data))
            # mongo.set_auth()

        elif arguments.system:

            s = OperatingSystem.get()
            print(Printer.attribute(s))

        return result
