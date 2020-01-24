from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.variables import Variables
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.management.configuration.arguments import Arguments
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters
from cloudmesh.common.console import Console
from cloudmesh.common.Printer import Printer
from cloudmesh.common.Shell import Shell
from cloudmesh.configuration.Config import Config
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import banner
import sys
from pathlib import Path
from pprint import pprint
import json
import os


class CheckCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_check(self, args, arguments):
        """
        ::

            Usage:
                check [KEYWORDS...] [--output=OUTPUT]


            Options:
               --output=OUTPUT  the output format [default: table]

            Description:

                checks if some programs are available to cms in the system. This
                includes

                    mongodb
                    ssh

                These can also be passed as optional keywords

        """

        map_parameters(arguments,
                       "output")

        variables = Variables()

        arguments.output = Parameter.find("output",
                                          arguments,
                                          variables,
                                          "table")

        keywords = arguments.KEYWORDS or ['mongo', "mongod", "mongoimport"]

        def check_ssh():
            cmd = "ssh " \
                  "-o StrictHostKeyChecking=no " \
                  "-o UserKnownHostsFile=/dev/null " \
                  f"-v localhost date"
            r = Shell.run(cmd)
            return "Connection refused" not in r

        def get_info(shell_command):
            v = "unkown"
            path = Shell.which(shell_command)
            if shell_command == "ssh":
                v = Shell.run(f"{shell_command} -V")
            elif path and len(path) > 0:
                try:
                    v = Shell.run(f"{shell_command} --version")
                    if shell_command.endswith("mongo"):
                        v = v.splitlines()[0].replace("MongoDB shell version ",
                                                      "")
                    elif shell_command.endswith("mongod"):
                        v = v.splitlines()[0].replace("db version ", "")
                    elif shell_command.endswith("mongoimport"):
                        v = v.splitlines()[0].replace("mongoimport version: ",
                                                      "")

                except:
                    v = "unkown"
            return path, v

        config = Config()
        try:
            machine = sys.platform
            mongo_path = config[
                f"cloudmesh.data.mongo.MONGO_DOWNLOAD.{machine}.MONGO_HOME"]
        except:
            mongo_path = None
        data = {}

        for keyword in keywords:

            #
            # probe system mongo
            #
            path, version_string = get_info(keyword)

            entry = {
                'system': {
                    'name': keyword,
                    'path': path,
                    'version': version_string
                }
            }

            data[keyword] = entry

            #
            # probe cloudmesh mongo
            #

            if "mongo" in ['mongo', 'mongod', 'mongoimport']:
                if mongo_path:

                    path = str(Path(path_expand(mongo_path)) / "bin" / keyword)

                    p, v = get_info(path)

                    try:

                        entry = {
                            'cloudmesh': {
                                'name': keyword,
                                'path': path,
                                'version': v
                            }
                        }

                    except:
                        Console.error(f"{keyword}")

                data[keyword].update(entry)

        path, v = get_info('ssh')
        data['ssh'] = {
            'system': {
                'name': 'ssh',
                'path': path,
                'version': v.strip(),
                'enabled': check_ssh()
            }
        }

        #
        # probe ssh commands
        #
        for c in ["ssh-keygen", "ssh-add", "ssh-agent"]:
            data[c] = {
                'system': {
                    'name': c,
                    'path': Shell.which(c),
                }
            }

        if len(data) > 0:
            banner("ssh, mongo, mongod, mongoimport")
            print(json.dumps(data, indent=2))

        banner("os.environ")
        for attribute in os.environ:
            print(attribute, os.environ[attribute])

        banner("Shell.run")

        for c in ["echo $0",
                  "echo $SHELL"]:
            try:
                r = Shell.run(c).strip()
            except:
                r = 'error'
            print(f"Shell.run('{c}')", r)

        return ""
