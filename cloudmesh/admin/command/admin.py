import textwrap

from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.dotdict import dotdict
from cloudmesh.configuration.Config import Config
from cloudmesh.management.configuration.operatingsystem import OperatingSystem
# from cloudmesh.admin.api.manager import Manager
from cloudmesh.mongo.MongoDBController import MongoDBController
from cloudmesh.mongo.MongoDBController import MongoInstaller
from cloudmesh.shell.command import PluginCommand, map_parameters
from cloudmesh.shell.command import command
from cloudmesh.common.debug import VERBOSE


class AdminCommand(PluginCommand):
    # noinspection PyPep8
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
            admin mongo install [--brew] [--download=PATH] [--nosudo] [--docker] [--dryrun] [--force]
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
            admin mongo list [--output=OUTPUT]
            admin mongo ssh
            admin mongo mode [MODE]
            admin status
            admin system info

          The admin command performs some administrative functions, such as
          installing packages, software and services. It also is used to
          start services and configure them.

          Arguments:
            FILENAME  the filename for backups

          Options:
            -f      specify the file

          Description:

            Mongo DB

              MongoDB is managed through a number of commands.

              The configuration is read from ~/.cloudmesh/cloudmesh.yaml

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

              The command

                cms admin mongo ssh

              is only supported for docker and allows for debugging to login
              to the running container. This function may be disabled in future.


            admin mongo mode native
               switches configuration file to use native mode

            admin mongo mode running
                switches the configuration to use running mode

        """

        map_parameters(arguments,
                       "output",
                       "nosudo",
                       "docker",
                       "dryrun",
                       "force")
        arguments.output = arguments.output or "table"

        VERBOSE(arguments)
        # arguments.PATH = arguments['--download'] or None
        result = None

        if arguments.mongo:

            if arguments.install and arguments.docker:

                installer = MongoInstaller(dryrun=arguments.dryrun,
                                           force=arguments.force)
                r = installer.docker()
                return r

            elif arguments.install:

                print("MongoDB install")
                print(79 * "=")
                # print(arguments.force)
                installer = MongoInstaller(dryrun=arguments.dryrun,
                                           force=arguments.force)

                sudo = not arguments.nosudo
                # if 'linux' in platform.lower() :
                #     print("SUDO:", sudo)
                # r = installer.install(sudo=sudo)
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
                        data["command"] = state['output'][pid][
                            'command'].strip()

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

            elif arguments.ssh:

                print("MongoDB ssh")
                MongoDBController().ssh()

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
                    if arguments.output == 'table':
                        print(Printer.dict(r, order=["name",
                                                     "sizeOnDisk",
                                                     "empty",
                                                     "collections"],
                                           output=arguments.output),
                              )
                    else:
                        print(Printer.write(r, output=arguments.output))
                    Console.ok("ok")
                else:
                    Console.ok("is your MongoDB server running")

            elif arguments.mode:

                if arguments.MODE:

                    if arguments.MODE not in ["native", "running", "docker"]:
                        Console.error("The mode is not supported")
                    config = Config()
                    config["cloudmesh.data.mongo.MODE"] = arguments.MODE
                    config.save()

                else:
                    config = Config()
                    mode = config["cloudmesh.data.mongo.MODE"]
                    print(mode)
                    return ""


        elif arguments.status:

            # config = Config()
            # data = config["cloudmesh.data.mongo"]

            print("Rest Service status")

            print("MongoDB status")

            try:
                mongo = MongoDBController()
                mongo.login()
                if mongo.status()['status'] == 'ok':
                    Console.ok("Mongo is running")
            except Exception as e:
                Console.error("Mongo is not running")
                print(e)

        elif arguments.system:

            s = OperatingSystem.get()
            print(Printer.attribute(s))

        return result
