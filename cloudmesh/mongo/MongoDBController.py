import os
import subprocess
import urllib.parse
from sys import platform

import yaml
from pymongo import MongoClient

from cloudmesh.common.Shell import Shell, Brew
from cloudmesh.common.console import Console
from cloudmesh.common.dotdict import dotdict
from cloudmesh.management.configuration.config import Config
from cloudmesh.management.script import Script, SystemPath
from cloudmesh.management.script import find_process


# noinspection PyUnusedLocal
class MongoInstaller(object):

    def __init__(self):
        """
        Initialization of the MOngo installer
        """

        self.config = Config()
        self.data = self.config.data["cloudmesh"]["data"]["mongo"]
        self.expanduser()

    #
    # TODO: This function seems duplicated
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
            print(
                "MongoDB is not installed in {MONGO_PATH}".format(**self.data))
            #
            # ask if you like to install and give info where it is being installed
            #
            # use cloudmesh yes no question see cloudmesh 3
            #
            print("Auto-install the MongoDB into {MONGO_PATH}".format(
                **self.data))

            self.data["MONGO_CODE"] = self.data["MONGO_DOWNLOAD"][platform]

            if platform.lower() == 'linux':
                self.linux()
            elif platform.lower() == 'darwin':
                self.darwin()
            elif platform.lower() == 'win32':  # Replaced windows with win32
                self.windows()
            else:
                print("platform not found", platform)

    # noinspection PyUnusedLocal
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
        wget -O /tmp/mongodb.tgz {MONGO_CODE}
        tar -zxvf /tmp/mongodb.tgz -C {LOCAL}/mongo --strip 1
        echo \"export PATH={MONGO_HOME}/bin:$PATH\" >> ~/.bashrc
            """.format(**self.data)
        installer = Script.run(script)

    # noinspection PyUnusedLocal
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
            installer = Script.run(script)
            SystemPath.add("{MONGO_HOME}/bin".format(**self.data))

            # THIS IS BROKEN AS ITS A SUPBROCESS? '. ~/.bashrc'

    def windows(self, brew=False):
        """
        install MongoDB in windows
        """
        # Added below code to change unix format to windows format for directory creation
        self.data["MONGO_HOME"] = self.data["MONGO_HOME"].replace("/", "\\")
        self.data["MONGO_PATH"] = self.data["MONGO_PATH"].replace("/", "\\")
        self.data["MONGO_LOG"] = self.data["MONGO_LOG"].replace("/", "\\")

        script = """
        mkdir {MONGO_PATH}
        mkdir {MONGO_HOME}
        mkdir {MONGO_LOG}
        msiexec.exe /l*v {MONGO_LOG}\mdbinstall.log  /qb /i {MONGO_CODE} INSTALLLOCATION={MONGO_PATH} ADDLOCAL="all"
        """.format(**self.data)
        installer = Script.run(script)


class MongoDBController(object):
    __shared_state = {}

    script_passwd = """
    use admin
    db.changeUserPassword("{MONGO_USERNAME}", "{MONGO_PASSWORD}")
    """

    script_admin = """
    
    use admin
    db.createUser(
      {
        user: "{MONGO_USERNAME}",
        pwd: "{MONGO_PASSWORD}",
        roles: [ { role: "userAdminAnyDatabase", db: "admin" }, "readWriteAnyDatabase" ]
      }
    )
    """

    """
    Steps to add admin
    
    1. start mongo
    mongod --port {MONGO_PORT} --bind_ip {MONGO_HOST} --dbpath {MONGO_PATH}/{MONGO_DBNAME}
    
    
    2. pip scriptadmin to 

    mongo --port 27017

    3. restart mongo
    
    mongod --auth --bind_ip {MONGO_HOST} --port {MONGO_PORT} --dbpath {MONGO_PATH}/{MONGO_DBNAME}
    
    """

    def __init__(self):

        self.__dict__ = self.__shared_state
        if "data" not in self.__dict__:
            self.config = Config()
            self.data = dotdict(self.config.data["cloudmesh"]["data"]["mongo"])
            self.expanduser()

            if self.data.MONGO_PASSWORD in ["TBD", "admin"]:
                Console.error("MongoDB password must not be the default")
                raise Exception("password error")
            mongo_path = self.data["MONGO_PATH"]
            mongo_log = self.data["MONGO_LOG"]
            paths = [mongo_path, mongo_log]
            for path in paths:
                if not os.path.exists(path):
                    os.makedirs(path)

    def login(self):
        host = self.data["MONGO_HOST"]
        port = int(self.data["MONGO_PORT"])
        password = str(self.data["MONGO_PASSWORD"])
        username = str(self.data["MONGO_USERNAME"])

        data = {
            'username': urllib.parse.quote_plus(username.encode()),
            'password': urllib.parse.quote_plus(password.encode())
        }
        connection = 'mongodb://{username}:{password}@127.0.0.1'.format(**data)
        client = MongoClient(connection)
        return client

    def list(self):
        client = self.login()

        data = {}
        for db in client.list_databases():
            data[db['name']] = db
        return data

    def __str__(self):
        return yaml.dump(self.data, default_flow_style=False, indent=2)

    def expanduser(self):
        for key in self.data:
            if type(self.data[key]) == str:
                self.data[key] = os.path.expanduser(self.data[key])
        # pprint(self.data)

    def update_auth(self):
        """
        create admin account in MongoDB
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

        print(
            "Enable the Security. You will use your username and password to login the MongoDB")

    def create(self):

        # Added special code for windows. Cant do start service and set_auth in same cms execution.

        if platform.lower() == 'win32':
            self.start(security=False)
        else:
            self.start(security=False)
            self.set_auth()
            self.stop()

    def start(self, security=True):
        """
        start the MongoDB server
        """
        auth = ""
        if security:
            auth = "--auth"

        if platform.lower() == 'win32':
            try:
                command = "-scriptblock { " + "mongod {auth} --bind_ip {MONGO_HOST} --dbpath {MONGO_PATH} --logpath {MONGO_LOG}/mongod.log".format(
                    **self.data, auth=auth) + " }"
                script = """
                powershell -noexit start-job {command}
                """.format(**self.data, command=command)
                Script.run(script)
                result = "child process started successfully. Program existing now"
            except Exception as e:
                result = "Mongo in windows could not be started." + str(e)
        else:
            try:
                script = "mongod {auth} --bind_ip {MONGO_HOST} --dbpath {MONGO_PATH} --logpath {MONGO_LOG}/mongod.log --fork".format(
                    **self.data, auth=auth)
                result = Script.run(script)

            except Exception as e:
                result = "Mongo could not be started." + str(e)

        if "child process started successfully" in result:
            print(Console.ok(result))
        else:
            print(Console.error(result))

    # noinspection PyMethodMayBeStatic
    def stop(self):
        """
        shutdown the MongoDB server
        linux and darwin have different way to shutdown the server, the common way is kill
        """
        # TODO: there  could be more mongos running, be more specific
        script = 'kill -2 `pgrep mongo`'
        result = Script.run(script)
        print(result)

    def set_auth(self):
        """
        add admin account into the MongoDB admin database
        """

        if platform.lower() == 'win32':
            script = """
            mongo --eval "db.getSiblingDB('admin').createUser({{user:'{MONGO_USERNAME}',pwd:'{MONGO_PASSWORD}',roles:[{{role:'root',db:'admin'}}]}})"
            """.format(**self.data)
            print(script)
        else:
            script = """mongo --eval 'db.getSiblingDB("admin").createUser({{user:"{MONGO_USERNAME}",pwd:"{MONGO_PASSWORD}",roles:[{{role:"root",db:"admin"}}]}})'""".format(
                **self.data)

        result = Script.run(script)
        print(result)

    def dump(self, filename):
        """

        :param filename: The filename

        dump the entire MongoDB database into output location

        """
        #
        # TODO: BUG: expand user
        #

        script = "mongodump --authenticationDatabase admin --archive={MONGO_HOME}/{filename}.gz --gzip -u {MONGO_USERNAME} -p {MONGO_PASSWORD}".format(
            **self.data, filename=filename)
        result = Script.run(script)
        print(result)

    def restore(self, filename):
        """

        :param filename: The filename

        restore the backup data generated by dump
        """
        #
        # TODO: BUG: expand user
        #

        script = "mongorestore --authenticationDatabase admin -u {MONGO_USERNAME} -p " \
                 "{MONGO_PASSWORD} --gzip --archive={MONGO_HOME}/{filename}.gz".format(**self.data, filename=filename)
        result = Script.run(script)
        print(result)

    def status(self):
        """
        check the MongoDB status
        returns a json object with status: and pid: command
        """

        if platform.lower() == 'win32':
            script = """
            tasklist /FO LIST /FI "IMAGENAME eq mongod.exe"
            """
            output = Script.run(script)
            result = {}
            for row in output.split('\n'):
                if ': ' in row:
                    key, value = row.split(': ')
                    result[key.strip()] = value.strip()

            if result is None:
                state = dotdict(
                    {"status": "error",
                     "message": "No mongod running",
                     "output": None
                     })
            else:
                state = dotdict(
                    {"status": "ok",
                     "message": "running",
                     "output": None
                     })
                process = {
                    "pid": str(result['PID']),
                    "command": result['Image Name']
                }
                output = {}
                #
                # TODO: there was a bug here, please check, it was only str()
                #
                output[str(result['PID'])] = process
                state["output"] = output

        else:
            result = find_process("mongod")
            if result is None:
                state = dotdict(
                    {"status": "error",
                     "message": "No mongod running",
                     "output": None
                     })
                output = None
            else:
                state = dotdict(
                    {"status": "ok",
                     "message": "running",
                     "output": None
                     })
                output = {}
                for p in result:
                    p = dotdict(p)
                    process = {
                        "pid": str(p.pid),
                        "command": p.command
                    }
                    output[str(p.pid)] = process
                state["output"] = output
        return state

    # noinspection PyBroadException
    def version(self):
        ver = None
        try:
            out = \
                subprocess.check_output("mongod --version", encoding='UTF-8',
                                        shell=True).split("\n")[0].split(
                    "version")[
                    1].strip().split(".")
            ver = (int(out[0][1:]), int(out[1]), int(out[2]))
        except Exception as e:
            return None
        return ver

    def stats(self):
        script = """mongo --eval 'db.stats()'""".format(**self.data)

        result = Script.run(script).split("\n")

        output = {}
        for line in result:
            line = line.replace("Implicit session: session {", "")
            line = line.replace(") }", "")
            line = line.replace("MongoDB shell version", "shell_version: ")
            line = line.replace("MongoDB server version:", "server_version: ")

            line = line.replace("connecting to", "endpoint")
            line = line.replace("UUID(", "")
            line = line.strip()
            line = line.replace("}", "")
            line = line.replace("{", "")
            if ":" in line:
                line = line.replace('"', "")
                line = line.replace(',', "")

                attribute, value = line.split(":", 1)
                output[attribute] = str(value).strip()

        return output


"""

# TODO: develop a nosetest for this

connection = pymongo.Connection(host = "127.0.0.1", port = 27017)
db = connection["test_db"]
test_collection = db["test_collection"]
db.command("dbstats") # prints database stats for "test_db"
db.command("collstats", "test_collection")
"""
