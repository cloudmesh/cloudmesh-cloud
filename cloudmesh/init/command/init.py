import os
import shutil
import sys
from pathlib import Path
from sys import exit
from sys import platform
import textwrap

from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import yn_choice
from cloudmesh.common.variables import Variables
from cloudmesh.configuration.Config import Config
from cloudmesh.mongo.MongoDBController import MongoDBController
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.mongo.CmDatabase import CmDatabase


class InitCommand(PluginCommand):

    # noinspection PyUnusedLocal,PyBroadException
    @command
    def do_init(self, args, arguments):
        """
        ::

            Usage:
                init [CLOUD] [--debug]
                init yaml

            Description:

                Initializes cloudmesh while using data from
                ~/.cloudmesh/cloudmesh.yaml.

                If no cloud is specified a number of local collections are
                created. If a cloud is specified it also uploads the
                information about images, flavors, vms. It also uploads the
                security groups defined by default to the cloud.

            Bug:

                cms init
                cms init

                    On Windows you have to run the cms init command twice upon
                    first installation
        """

        ssh_key = path_expand("~/.ssh/id_rsa.pub")
        if not os.path.exists(ssh_key):
            Console.error(f"The ssh key {ssh_key} does not exist.")
            print()

            Console.info(
                "cms init is a convenient program to set up cloudmesh"
                " with defaukt values. Please make sure you use ssh-keygen"
                " to set up the keys.\n\n"
                "      Additionally we recommend that you use. \n\n"
                "        cms test\n\n"
                "      to identify other issues\n")
            return ""

        config = Config()

        if config["cloudmesh.profile.user"] == "TBD":
            Console.info(
                "cms init is a convenient program to set up cloudmesh"
                " with defaukt values. Please make sure you use in your"
                " ~/.cloudmesh/yaml file a valid value for\n\n"
                "        cloudmesh.profile.user\n\n"
                "      This name is aslo used as keyname in the cloud providers\n\n"
                "      Additionally we recommend that you use. \n\n"
                "        cms test\n\n"
                "      to identify other issues\n")
            return ""

        if arguments.CLOUD == "yaml":

            location = path_expand("~/.cloudmesh/cloudmesh.yaml")
            path = Path(location)
            if path.is_file():
                print()
                if yn_choice(
                    "The file ~/.cloudmesh/cloudmesh.yaml exists, do you wnat to overwrite it",
                    default='n'):
                    config.fetch()
                    print()
                    Console.ok("File cloudmesh.yaml downloaded from Github")
                else:
                    print()
                    Console.warning("Download canceled")
                print()

        else:
            variables = Variables()

            if config["cloudmesh.data.mongo.MODE"] != 'running':
                try:
                    print("MongoDB stop")
                    MongoDBController().stop()
                except:
                    Console.ok("MongoDB is not running. ok")
                machine = platform.lower()
                location = path_expand(config[
                                           f'cloudmesh.data.mongo.MONGO_DOWNLOAD.{machine}.MONGO_PATH'])
                try:
                    print("deleting:", location)
                    shutil.rmtree(location)
                    print("MongoDB folder deleted")
                except Exception as e:
                    Console.error(f"Could not delete {location}")
                    if platform == 'win32':
                        print(e)
                        Console.error(f"Please try to run cms init again ... ")
                        return ""

                print("MongoDB create")
                os.system("cms admin mongo create")
                os.system("cms admin mongo start")
            else:
                print("MongoDB is on \"running\" mode!")
                print("Dropping cloudmesh database...")
                cm_db = CmDatabase()
                cm_db.connect()
                cm_db.drop_database()

            user = config["cloudmesh.profile.user"]

            secgroup = "flask"

            print("Set key")
            if user == "TBD":
                Console.error(
                    "the user is not set in the yaml file for cloudmesh.profile.user")
                sys.exit()

            variables["key"] = user

            Console.ok("Config Security Initialization")
            Shell.execute("cms", ["config", "secinit"])

            os.system("cms key add")
            os.system("cms sec load")

            if arguments.CLOUD is not None:
                cloud = arguments.CLOUD

                variables['cloud'] = cloud
                os.system(f"cms key upload {user} --cloud={cloud}")
                os.system(f"cms flavor list --refresh")
                os.system(f"cms image list --refresh")
                os.system(f"cms vm list --refresh")
                os.system(f"cms sec group load {secgroup} --cloud={cloud}")
                os.system(f"cms set secgroup={secgroup}")

            if arguments.debug:
                variables['debug'] = True
                variables['timer'] = 'on'
                variables['trace'] = True
                variables['verbose'] = '10'

            print()
            print("Variables")
            print()
            for name in variables:
                value = variables[name]
                print(f"    {name}={value}")
