from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
# from cloudmesh.admin.api.manager import Manager
from cloudmesh.mongo.MongoDBController import MongoDBController
from cloudmesh.mongo.MongoDBController import MongoInstaller
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
import textwrap
from pprint import pprint
from cloudmesh.common.dotdict import dotdict

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
            admin mongo status
            admin mongo stats
            admin mongo version
            admin mongo start
            admin mongo stop
            admin mongo backup FILENAME
            admin mongo load FILENAME
            admin mongo security
            admin mongo password PASSWORD
            admin rest status
            admin rest start
            admin rest stop
            admin status

          The admin command performs some adminsitrative functions, such as installing packages, software and services.
          It also is used to start services and configure them.

          Arguments:
            FILENAME  the filename for backups

          Options:
            -f      specify the file

          Description:

            TBD

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

            elif arguments.start:

                print("MongoDB start")
                MongoDBController().start(False)

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

        return result
