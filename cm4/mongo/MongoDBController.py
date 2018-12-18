import os
import yaml
from sys import platform
from cm4.configuration.config import Config
from pprint import pprint
from cm4.common.script import Script, SystemPath
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.Shell import Shell, Brew
from cloudmesh.common.console import Console

import subprocess

class MongoInstaller(object):

    def __init__(self):
        """
        Initialization of the MOngo installer
        """

        self.config = Config()
        self.data = self.config.data["cloudmesh"]["data"]["mongo"]
        self.expanduser()

    #
    # TODO: THis function seems duplicated
    #
    def expanduser(self):
        for key in self.data:
            if type(self.data[key]) == str:
                self.data[key] = os.path.expanduser(self.data[key])
        # pprint(self.data)

    def __str__(self):
        return yaml.dump(self.data, default_flow_style=False, indent=2)

    def install(self):
        """
        check where the MongoDB is installed in mongo location.
        if MongoDB is not installed, python help install it
        """
        path = os.path.expanduser(self.data["MONGO_PATH"])
        print(path)
        # pprint(self.data)

        if not self.data["MONGO_AUTOINSTALL"]:
            print("Mongo auto install is off")
            return ""

        if not os.path.isdir(path) and self.data["MONGO_AUTOINSTALL"]:
            print("MongoDB is not installed in {MONGO_PATH}".format(**self.data))
            #
            # ask if you like to install and give infor wher it is being installed
            #
            # use cloudmesh yes no question see cloudmesh 3
            #
            print("Auto-install the MongoDB into {MONGO_PATH}".format(**self.data))

            self.data["MONGO_CODE"] = self.data["MONGO_DOWNLOAD"][platform]

            if platform.lower() == 'linux':
                self.linux()
            elif platform.lower() == 'darwin':
                self.darwin()
            elif platform.lower() == 'windows':
                self.windows()
            else:
                print("platform not found", platform)

    def linux(self):
        # TODO UNTESTED
        """
        install MongoDB in Linux system (Ubuntu)
        """
        script = """
        sudo apt-get --yes install libcurl4 openssl
        mkdir -p {MONGO_PATH}
        mkdir -p {MONGO_HOME}
        mkdir -p {MONGO_LOG}
        wget -P /tmp/mongodb.tgz {MONGO_CODE}
        tar -zxvf /tmp/mongodb.tgz -C {LOCAL}/mongo --strip 1
            """.format(**self.data)
        installer = Script(script)
        SystemPath.add("{MONGO_HOME}/bin".format(**self.data))

        # THIS IS BROKEN AS ITS A SUPBROCESS? '. ~/.bashrc'

    def darwin(self, brew=False):
        """
        install MongoDB in Darwin system (Mac)
        """

        if brew:
            print("mongo installer via brew")
            Brew.install("mongodb")
            path = Shell.which("mongod")
            SystemPath.add("{path}".format(path=path))

        else:
            script = """
            mkdir -p {MONGO_PATH}
            mkdir -p {MONGO_HOME}
            mkdir -p {MONGO_LOG}
            curl -o /tmp/mongodb.tgz {MONGO_CODE}
            tar -zxvf /tmp/mongodb.tgz -C {LOCAL}/mongo --strip 1
            """.format(**self.data)
            installer = Script(script)
            SystemPath.add("{MONGO_HOME}/bin".format(**self.data))

            # THIS IS BROKEN AS ITS A SUPBROCESS? '. ~/.bashrc'

    def windows(self, brew=False):
        """
        install MongoDB in Darwin system (Mac)
        """

        """

        preferred container and linux subsystem

        We wnat to capture multiple solutions. We only support Windows 10 

        check for newest version of windows
  
        a) container based

           This worksonly on proper versions of windows 10, not home, e.g. edu and pro
    
        b) regular install
           
           https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/

        c) linux subsystem

        https://docs.microsoft.com/en-us/windows/wsl/install-win10 
        ubuntu 18.04


        d) MOngoDB in the cloud, while making sure credentials are not in the db

        https://www.mongodb.com/cloud/atlas?utm_source=install-mongodb-on-windows&utm_campaign=20-docs-in-20-days&utm_medium=docs

        e) Chameleon cloud or any other cloud via cloudmesh

        """
        # TODO
        raise NotImplementedError


class MongoDBController(object):

    def __init__(self):

        self.config = Config()
        self.data = dotdict(self.config.data["cloudmesh"]["data"]["mongo"])
        self.expanduser()

        if self.data.MONGO_PASSWORD in ["TBD", "admin"]:
            Console.error("MongoDB password must not be the default")
            raise Exception("password error")

    def __str__(self):
        return yaml.dump(self.data, default_flow_style=False, indent=2)

    def expanduser(self):
        for key in self.data:
            if type(self.data[key]) == str:
                self.data[key] = os.path.expanduser(self.data[key])
        pprint(self.data)

    def update_auth(self):
        """
        create admin acount in MongoDB
        """
        #
        # TODO: BUG: should that not be done differently, e.g. from commandline or via ENV variables
        #
        # run mongodb

        self.start(True)

        # set up auth information
        self.set_auth()

        # shut down mongodb
        self.stop()

        print("Enable the Secutiry. You will use your username and password to login the MongoDB")

    def start(self, no_security=False):
        """
        start the MongoDB server
        """
        auth = ""
        if not no_security:
            auth = "--auth"

        script = "mongod {auth} --bind_ip {MONGO_HOST} --dbpath {MONGO_PATH} --logpath {MONGO_LOG}/mongod.log --fork".format(**self.data, auth=auth)

        print(script)
        run = Script(script)

    # noinspection PyMethodMayBeStatic
    def stop(self):
        """
        shutdown the MongoDB server
        linux and darwin have different way to shutdown the server, the common way is kill
        """
        script = 'kill -2 `pgrep mongo`'
        run = Script(script)

    def set_auth(self):
        """
        add admin acount into the MongoDB admin database
        """

        script = """mongo --eval 'db.getSiblingDB("admin").createUser({user:"{MONGO_USERNAME}",pwd:"{MONGO_PASSWORD}",roles:[{role:"root",db:"admin"}]})'""".format(**self.data)

        run = Script(script)

    def dump(self, filename):
        """
        dump the entire MongoDB database into output location
        :param output_location: the location to save the backup
        """
        #
        # TODO: BUG: expand user
        #

        script = "mongodump --authenticationDatabase admin --archive={MONGO_HOME}/{filename}.gz --gzip -u {MONGO_USERNAME} -p {MONGO_PASSWORD}".format(**self.data, filename=filename)
        run = Script(script)

    def restore(self, filename):
        """
        restore the backup data generated by dump
        :param data: the backup data folder
        """
        #
        # TODO: BUG: expand user
        #

        script = "mongorestore --authenticationDatabase admin -u {MONGO_USERNAME} -p " \
                 "{MONGO_PASSWORD} --gzip --archive={MONGO_HOME}/{filename}.gz".format(**self.data, filename=filename)
        run = Script(script)

    def status(self):
        """
        check the MongoDB status
        """

        script = "ps -ax | grep mongo | fgrep -v grep"

        ps_output = Script(script)
        print(ps_output)


    def version(self):
        ver = None
        try:
            out = subprocess.check_output("mongod --version", encoding='UTF-8', shell=True).split("\n")[0].split("version")[1].strip().split(".")
            ver = (int(out[0][1:]), int(out[1]), int(out[2]))
        except:
            return None
        return ver
