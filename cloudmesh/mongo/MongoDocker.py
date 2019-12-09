#
# Author: Gregor von Laszewski, laszewski@gmail.com
#

from cloudmesh.configuration.Config import Config
from cloudmesh.common.util import path_expand
from cloudmesh.management.script import Script, SystemPath
from cloudmesh.management.script import find_process
from cloudmesh.common.console import Console
import os
import time
import sys
import shutil
from progress.bar import Bar
from cloudmesh.common.dotdict import dotdict


class MongoDocker(object):

    def __init__(self, configuration="~/.cloudmesh/cloudmesh.yaml",
                 dryrun=False):
        path = path_expand(configuration)
        self.config = Config(config_path=path)
        self.data = self.config["cloudmesh.data.mongo"]

        self.NAME = "cloudmesh-mongo"

        self.username = self.data["MONGO_USERNAME"]
        self.password = self.data["MONGO_PASSWORD"]
        self.port = self.data["MONGO_PORT"]
        self.host = self.data["MONGO_HOST"]
        self.dryrun = dryrun
        self.mongo_path = path_expand(
            self.data["MONGO_DOWNLOAD"]["docker"]["MONGO_PATH"])
        self.mongo_log = path_expand(
            self.data["MONGO_DOWNLOAD"]["docker"]["MONGO_LOG"])
        self.version = self.data["MONGO_DOWNLOAD"]["docker"]["version"]

        self.flag_name = "--name cloudmesh-mongo"
        self.flag_data = f"-v {self.mongo_path}:/data/db"
        self.flag_log = f"-v {self.mongo_log}/mongod.log:/var/log/mongodb/mongodb.log"
        self.flag_dot_cloudmesh = f"-v ~/.cloudmesh:/root/.cloudmesh"
        self.flag_dot_ssh = f"-v ~/.ssh:/root/.ssh"

    def run(self, script, verbose=True, terminate=False):
        if verbose:
            Console.msg(script)

        if self.dryrun:
            return "dryrun"
        else:

            try:
                installer = Script.run(script, debug=False)
                if verbose:
                    print(installer)
                return installer
            except Exception as e:
                if verbose:
                    Console.error("Script returned with error")
                    print(e)
                if terminate:
                    sys.exit()
                return "error"

    def create(self):
        """
        Starts the MongoDBd Container
        :return:
        """
        script = f"docker run -d -p 127.0.0.1:27017:27017/tcp {self.flag_data} {self.flag_log} {self.flag_name} mongo"
        id = self.run(script, verbose=True)

        Console.ok("Starting docker mongo container with id")
        Console.msg("")
        Console.msg(f"   {id}")
        Console.msg("")

    def ssh(self, auth=True):
        """
        Starts the MongoDBd Container
        :return:
        """

        if auth:
            auth_flag = "--auth"
        else:
            auth_flag = ""
        script = f"docker exec -it {self.NAME} bash"
        os.system(script)

    def start(self, auth=True):
        """
        Starts the MongoDBd Container
        :return:
        """

        if auth:
            auth_flag = "--auth"
        else:
            auth_flag = ""
        script = f"docker run -d -p 127.0.0.1:27017:27017/tcp {self.flag_dot_ssh} {self.flag_dot_cloudmesh} {self.flag_data} {self.flag_log} {self.flag_name} mongo {auth_flag}"
        id = self.run(script)

        Console.ok("Starting docker mongo container with id")
        Console.msg("")
        Console.msg(f"   {id}")
        Console.msg("")
        print(script)

    def execute(self, command, auth=False, terminate=False, verbose=False):
        """
        Starts the MongoDBd Container
        :return:
        """

        auth_flag = "--auth"
        if not auth:
            auth_flag = ""

        script = f"docker exec {self.NAME} mongo admin {auth_flag} --eval {command}"
        result = self.run(script, verbose=verbose, terminate=terminate)
        return result

    def sh(self, command):
        script = f'docker exec cloudmesh-mongo {command}'
        self.run(script)

    def stop(self):
        """
        Stops the MongoDBd Container
        :return:
        """
        try:
            script = \
                f"docker stop {self.NAME}"
            self.run(script)
        except:
            pass

    def wait(self, delay=20, verbose=False):
        """
        test if mongo is available
        :return:
        """
        bar = Bar('Cloudmesh Docker Setup', max=delay)
        for i in range(delay):
            try:
                result = self.execute(
                    "\"printjson(db.adminCommand('listDatabases'))\"",
                    terminate=False,
                    verbose=verbose)
                if verbose:
                    print(result)
                if '"ok"' in result:
                    bar.finish()
                    return
            except Exception as e:
                if verbose:
                    print(e)
                pass
            bar.next()
            time.sleep(1)

    def create_admin(self):
        """
        Creates the admin user in the Container
        :return:
        """
        script = \
            f"docker exec {self.NAME}  mongo admin --eval " \
            '"' \
            "db.getSiblingDB('admin').createUser({" \
            f"user:'{self.username}'," \
            f"pwd:'{self.password}'," \
            "roles:[{role:'root',db:'admin'}]}); " \
            "db.shutdownServer();" \
            '"'
        os.system(script)

    def kill(self, name=None):
        """
        Kills all Containers
        :return:
        """
        try:
            if name is None:
                name = self.NAME
            script = f"docker container ls -aq --filter name={name}"
            id = self.run(script, verbose=False)

            if id != "":
                Console.msg(f"Kill container with id: {id}")
                script = \
                    f"docker stop {id}" \
                    f"docker rm {id}"
                self.run(script, verbose=False)
        except:
            Console.ok("No container found.")

    def ps(self):
        """
        Creates the Mongo image
        :return:
        """

        # script = \
        #    f"docker build . -t {self.NAME}"

        script = \
            f"docker ps"
        result = self.run(script, verbose=False)
        return result

    def install(self, clean=False, pull=True):
        """
        Creates the Mongo image
        :return:
        """

        Console.msg(f"Version: {self.version}")
        if pull:
            script = f"docker pull mongo:{self.version}"
            self.run(script)
        if clean:
            try:
                shutil.rmtree(self.mongo_path)
            except:
                pass
            try:
                shutil.rmtree(self.mongo_log)
            except:
                pass

        try:
            os.mkdir(self.mongo_path)
        except FileExistsError:
            Console.info(f"Folder {self.mongo_path} already exists")
        try:
            os.mkdir(self.mongo_log)
        except FileExistsError:
            Console.info(f"Folder {self.mongo_log} already exists")

    def login(self):
        os.system("docker exec -it cloudmesh-mongo bash")

    def initialize(self):
        self.kill()
        self.install(clean=True, pull=True)
        self.create()
        self.wait(verbose=False)
        self.create_admin()
        self.kill()

    def status(self, auth=False):
        """
        Status of the the MongoDB Container
        :return: DIct with the status
        """
        msg = "No mongod running"
        state = "error"

        print("XXX")
        try:
            result = self.execute(
                "\"printjson(db.adminCommand('listDatabases'))\"",
                terminate=False,
                auth=auth,
                verbose=False)
            if '"ok"' in result:
                state = "ok"
                msg = "running"
            print(result)
        except Exception as e:
            print(e)
            pass

        result = dotdict(
            {"status": state,
             "message": msg,
             "output": None
             })
        return result


if __name__ == "__main__":
    mongo = MongoDocker()

    # mongo = MongoDocker(dryrun=True)

    mongo.initialize()

    # mongo.sh("ps -e | grep mongo")

    mongo.start()
    mongo.wait()

    mongo.ps()

    mongo.kill()
