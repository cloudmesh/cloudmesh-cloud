import os.path
import shutil

from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from cloudmesh.common.variables import Variables
from cloudmesh.management.configuration.config import Config
from cloudmesh.mongo.MongoDBController import MongoDBController
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters


class InitCommand(PluginCommand):

    # noinspection PyUnusedLocal,PyBroadException
    @command
    def do_init(self, args, arguments):
        """
        ::

            Usage:
                init [CLOUD] [--debug]

            Description:

                Initializes cloudmesh while using data from
                ~/.cloudmesh/cloudmesh4.yaml.

                If no cloud is specified a number of local collections are
                created. If a cloud is specified it also uploads the
                information about images, flavors, vms. It also uploads the
                security groups defined by default to the cloud.

        """

        StopWatch.start("cms init")
        map_parameters(arguments, 'debug')

        variables = Variables()

        try:
            print("MongoDB stop")
            MongoDBController().stop()
        except:
            Console.ok("MongoDB is not running. ok")

        location = path_expand('~/.cloudmesh/mongodb')
        try:
            print("MongoDB delete")
            shutil.rmtree(location)
        except:
            Console.error(f"deleting {location}")

        user = Config()["cloudmesh.profile.user"]
        secgroup = "flask"

        print("MongoDB create")
        os.system("cms admin mongo create")
        os.system("cms admin mongo start")
        os.system(f"cms sec load")
        os.system(f"cms key add {user} --source=ssh")

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

        StopWatch.stop("cms init")

        StopWatch.benchmark(sysinfo=False)
