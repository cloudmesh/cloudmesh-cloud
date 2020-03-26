import ctypes
import json
import os
import subprocess
import urllib.parse
import urllib.parse
import urllib.parse
from sys import platform
from pathlib import Path
from subprocess import STDOUT
import ctypes

import psutil
import yaml
from cloudmesh.common.Shell import Shell, Brew
from cloudmesh.common.console import Console
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.util import path_expand
from cloudmesh.common.Shell import Shell
from cloudmesh.configuration.Config import Config
from cloudmesh.management.script import Script, SystemPath
from cloudmesh.management.script import find_process
from cloudmesh.common.Shell import Shell
from cloudmesh.common.debug import VERBOSE

# from cloudmesh.mongo.MongoDBController import MongoDBController
from pymongo import MongoClient
import sys


# noinspection PyUnusedLocal
class MongoInstaller(object):

    def __init__(self, dryrun=False, force=False):
        """
        Initialization of the MOngo installer
        """

        self.dryrun = dryrun
        self.force = force
        self.config = Config()
        self.data = self.config.data["cloudmesh"]["data"]["mongo"]
        self.machine = platform.lower()
        download = self.config[
            f"cloudmesh.data.mongo.MONGO_DOWNLOAD.{self.machine}"]

        self.mongo_code = path_expand(download["url"])
        self.mongo_path = path_expand(download["MONGO_PATH"])
        self.mongo_log = path_expand(download["MONGO_LOG"])
        self.mongo_home = path_expand(download["MONGO_HOME"])

        if self.dryrun:
            print(self.mongo_path)
            print(self.mongo_log)
            print(self.mongo_home)
            print(self.mongo_code)

    def __str__(self):
        return yaml.dump(self.data, default_flow_style=False, indent=2)

    def docker(self):
        username = self.data["MONGO_USERNAME"]
        password = self.data["MONGO_PASSWORD"]
        port = self.data["MONGO_PORT"]
        host = self.data["MONGO_HOST"]
        script = \
            f"docker run -d -p {host}:{port}:{port}" \
            f" --name cloudmesh-mongo" \
            f" -e MONGO_INITDB_ROOT_USERNAME={username}" \
            f" -e MONGO_INITDB_ROOT_PASSWORD={password}" \
            f" mongo"

        installer = Script.run(script)
        print(installer)

    def install(self, sudo=True):
        """
        check where the MongoDB is installed in mongo location.
        if MongoDB is not installed, python help install it
        """
        if self.dryrun:
            print(self.mongo_path)
        # pprint(self.data)

        mode = self.data['MODE']

        if mode == 'docker':
            Console.error("* Docker is not yet supported")
            self.docker()
            return ""

        if not self.data["MONGO_AUTOINSTALL"]:
            Console.error("Mongo auto install is off")
            print("You can set it with")
            print()
            Console.ok(
                "    cms config set cloudmesh.data.mongo.MONGO_AUTOINSTALL=True")
            print()
            if self.machine == 'darwin':
                print("To install it with brew you need to set also")
                print()
                Console.ok(
                    "    cms config set cloudmesh.data.mongo.MONGO_BREWINSTALL=True")
                print()

            return ""

        #
        # the path test may be wrong as we need to test for mongo and mongod
        #
        # print ('OOO', os.path.isdir(path), self.data["MONGO_AUTOINSTALL"] )
        if self.force or (not os.path.isdir(self.mongo_home) and self.data[
            "MONGO_AUTOINSTALL"]):
            print(f"MongoDB is not installed in {self.mongo_home}")
            #
            # ask if you like to install and give info where it is being installed
            #
            # use cloudmesh yes no question see cloudmesh 3
            #
            # print(f"Auto-install the MongoDB into {mongo_path}")

            self.local = self.data["LOCAL"]
            if self.machine == 'linux':
                self.linux()
            elif self.machine == 'darwin':
                self.darwin()
            elif self.machine == 'win32':  # Replaced windows with win32
                self.windows()
            else:
                print("platform not found", platform)
        elif os.path.isdir(self.mongo_home):
            Console.error(f"Folder {self.mongo_home} already exists")

    # noinspection PyUnusedLocal
    def linux(self, sudo=True):
        cmd = ['lsb_release', '-a']
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        o, e = proc.communicate()
        p = o.decode('ascii').replace('\t', "").splitlines()

        distro = "none"
        version = "none"

        for x in range(0, len(p)):
            s = p.pop(0)
            if "Distributor" in s:
                if "Debian" in s:
                    distro = "debian"
                elif "Ubuntu" in s:
                    distro = "ubuntu"
            elif "Release" in s:
                version = s.split(":").pop(1).split(".").pop(0)
        if "debian" == distro:
            self.debian(sudo, int(version))
        elif "ubuntu" == distro:
            self.ubuntu()
        else:
            Console.error("Unsupported Linux Version")
            raise Exception("unsupported version")

    def debian(self, sudo=True, version=10):
        """
        Install MongoDB in Linux Debian (9,10)
        """
        if sudo:
            sudo_command = "sudo"
        else:
            sudo_command = ""

        apt_cmd = "error"
        if version == 9:
            apt_cmd = "apt-get --yes install openssl libcurl3"
        elif version == 10:  # UNTESTED
            apt_cmd = "apt-get --yes install openssl libcurl4"
        else:
            Console.error("Unsupported Linux Version")
            raise Exception("unsupported operating system")

        script = f"{sudo_command} " + f"{apt_cmd} " + """
        mkdir -p {MONGO_PATH}
        mkdir -p {MONGO_HOME}
        mkdir -p {MONGO_LOG}
        wget -q -O /tmp/mongodb.tgz {MONGO_CODE}
        tar -zxvf /tmp/mongodb.tgz -C {LOCAL}/mongo --strip 1
        echo \"export PATH={MONGO_HOME}/bin:$PATH\" >> ~/.bashrc
            """.format(**self.data)
        installer = Script.run(script)

    def ubuntu(self):
        """
        install MongoDB in Linux system (Ubuntu)
        """
        # check if openssl and curl is installed
        chk_script = "openssl version && curl --version"
        Script.run(chk_script)

        script = f"""
        mkdir -p {self.mongo_path}
        mkdir -p {self.mongo_home}
        mkdir -p {self.mongo_log}
        wget -q -O /tmp/mongodb.tgz {self.mongo_code}
        tar -zxvf /tmp/mongodb.tgz -C {self.local}/mongo --strip 1
        echo \"export PATH={self.mongo_home}/bin:$PATH\" >> ~/.bashrc
            """
        if self.dryrun:
            print(script)
        else:
            installer = Script.run(script)

        Console.info("MongoDB installation successful!")

    # noinspection PyUnusedLocal
    def darwin(self, brew=False):
        """
        install MongoDB in Darwin system (Mac)
        """

        if brew:
            print("mongo installer via brew")
            if not self.dryrun:
                Brew.install("mongodb")
                path = Shell.which("mongod")
                SystemPath.add(f"{path}")

        else:
            script = f"""
            mkdir -p {self.mongo_path}
            mkdir -p {self.mongo_home}
            mkdir -p {self.mongo_log}
            curl -o /tmp/mongodb.tgz {self.mongo_code}
            tar -zxvf /tmp/mongodb.tgz -C {self.local}/mongo --strip 1
            """

            print(script)

            if self.dryrun:
                print(script)
            else:
                installer = Script.run(script)
                SystemPath.add(f"{self.mongo_home}/bin".format(**self.data))

            # THIS IS BROKEN AS ITS A SUPBROCESS? '. ~/.bashrc'
            Console.info("MongoDB installation successful!")

    def windows(self):
        """
        install MongoDB in windows
        """
        # Added below code to change unix format to windows format for directory creation
        # self.data["MONGO_HOME"] = self.data["MONGO_HOME"].replace("/", "\\")
        # self.data["MONGO_PATH"] = self.data["MONGO_PATH"].replace("/", "\\")
        # self.data["MONGO_LOG"] = self.data["MONGO_LOG"].replace("/", "\\")

        # def is_admin():
        #    try:
        #        if platform == 'win32':
        #            return ctypes.windll.shell32.IsUserAnAdmin()
        #    except:
        #        return False

        # noinspection PyPep8

        try:
            os.mkdir(self.mongo_home)
        except FileExistsError:
            Console.info(f"Folder {self.mongo_home} already exists")
        except FileNotFoundError:  # means you don't have enough privilege
            Console.error("Permission denied, requesting admin access")
            import win32com.shell.shell as shell
            script = f'mkdir "{self.mongo_home}"'
            shell.ShellExecuteEx(lpVerb='runas', lpFile='cmd.exe',
                                 lpParameters='/c ' + script)

        try:
            os.mkdir(self.mongo_path)
        except FileExistsError:
            Console.info(f"Folder {self.mongo_path} already exists")
        try:
            os.mkdir(self.mongo_log)
        except FileExistsError:
            Console.info(f"Folder {self.mongo_log} already exists")
        script = f"""msiexec.exe /l*v {self.mongo_log}/mdbinstall.log  /qb /i {self.mongo_code} INSTALLLOCATION="{self.mongo_home}" ADDLOCAL="all" """
        print(script)
        if self.dryrun:
            print(script)
        else:
            print(script)
            installer = Script.run(script)

            Console.info("MongoDB installation successful!")


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

    def __init__(self, dryrun=False):

        self.__dict__ = self.__shared_state
        if "data" not in self.__dict__:

            self.config = Config()
            self.data = dotdict(self.config.data["cloudmesh"]["data"]["mongo"])
            self.machine = platform.lower()
            download = self.config[
                f"cloudmesh.data.mongo.MONGO_DOWNLOAD.{self.machine}"]

            self.mongo_code = path_expand(download["url"])
            self.mongo_path = path_expand(download["MONGO_PATH"])
            self.mongo_log = path_expand(download["MONGO_LOG"])
            self.mongo_home = path_expand(download["MONGO_HOME"])

            if dryrun:
                print(self.mongo_path)
                print(self.mongo_log)
                print(self.mongo_home)
                print(self.mongo_code)

            if self.data.MONGO_PASSWORD in ["TBD", "admin"]:
                Console.error("MongoDB password must not be the default: TBD")

                raise Exception("password error")

            # mongo_log = self.data["MONGO_LOG"]
            paths = [self.mongo_path, self.mongo_log]
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
            name = db['name']
            data[name] = db
            names = client[name].collection_names()
            data[name]['collections'] = names

            # data[name]['collections'] = {}
            # collections = data[name]['collections']
            # collections = names
            # for collection_name in names:
            #    entry = {'name': collection_name}
            #    collections[collection_name] = entry

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
            Console.info("Starting mongo without authentication ... ")
            self.start(security=False)
            Console.info("Creating admin user ... ")
            self.set_auth()
            Console.info("Stopping the service ... ")
            self.stop()
        else:
            Console.info("Starting mongo without authentication ... ")
            self.start(security=False)
            Console.info("Creating admin user ... ")
            self.set_auth()
            Console.info("Stopping the service ... ")
            self.stop()

    def import_collection(self, security=True):
        mongo_host = self.data['MONGO_HOST']
        auth = ""
        if security:
            auth = "--auth"
        command = f"mongoimport {auth} --bind_ip {mongo_host} --dbpath {self.mongo_path} --logpath {self.mongo_log}/mongod.log" \
                  " --fork".format(**self.data, auth=auth)

    def start(self, security=True):
        """
        start the MongoDB server
        """
        mode = self.data['MODE']

        if mode == 'docker':
            Console.error("* Docker is not yet supported")
            raise NotImplementedError

        auth = ""
        if security:
            auth = "--auth"
        mongo_host = self.data['MONGO_HOST']
        if platform.lower() == 'win32':
            try:
                # command = 'where mongo'
                # proc = subprocess.Popen(command, shell=True,
                #                        stdin=subprocess.PIPE,
                #                        stdout=subprocess.PIPE)
                # out, err = proc.communicate()

                # print ("MMM", command)
                # print ("O", out)
                # print ("E", err)

                # if out == b'':
                #    Console.error("mongo command not found")
                #    sys.exit()
                mongo_runner = f"\"{self.mongo_home}\\bin\mongod\" {auth} " \
                               f"--bind_ip {mongo_host}" \
                               f" --dbpath \"{self.mongo_path}\" --logpath \"{self.mongo_log}\mongod.log\""
                print(mongo_runner)
                if not os.path.isfile(f'{self.mongo_path}/invisible.vbs'):
                    with open(f'{self.mongo_path}/invisible.vbs', 'w') as f:
                        f.write(
                            'CreateObject("Wscript.Shell").Run """" & WScript.Arguments(0) & """", 0, False')
                if not os.path.isfile(f'{self.mongo_path}/mongo_starter.bat'):
                    with open(f'{self.mongo_path}/mongo_starter.bat', 'w') as f:
                        f.write(mongo_runner)
                script = f'wscript.exe \"{self.mongo_path}/invisible.vbs\" \"{self.mongo_path}/mongo_starter.bat\"'
                print(script)
                p = subprocess.Popen(script, shell=True, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
                result = "mongod child process should be started successfully."
            except Exception as e:
                result = "Mongo in windows could not be started: \n\n" + str(e)
        else:
            try:
                script = f"mongod {auth} --bind_ip {mongo_host}" \
                         f" --dbpath {self.mongo_path} --logpath {self.mongo_log}/mongod.log --fork"
                result = Script.run(script)

            except Exception as e:
                result = "Mongo could not be started." + str(e)

        if "successfully" in result:
            print(Console.ok(result))
        else:
            print(Console.error(result))

    # noinspection PyMethodMayBeStatic
    def stop(self):
        """
        shutdown the MongoDB server
        linux and darwin have different way to shutdown the server, the common way is kill
        """
        mode = self.data['MODE']

        if mode == 'docker':
            Console.error("* Docker is not yet supported")
            raise NotImplementedError

        # TODO: there  could be more mongos running, be more specific
        if platform.lower() == 'win32':
            MONGO = f"\"{self.mongo_home}\\bin\mongo\""
            script = f'{MONGO} --eval "db.getSiblingDB(\'admin\').shutdownServer()"'
            p1 = subprocess.Popen(script, shell=True, stdout=subprocess.PIPE,
                                  stderr=STDOUT)
            MONGO_USERNAME = self.data['MONGO_USERNAME']
            MONGO_PASSWORD = self.data['MONGO_PASSWORD']
            shutdown_with_auth1 = f"""{MONGO} -u {MONGO_USERNAME} -p {MONGO_PASSWORD} --eval "db.getSiblingDB(\'admin\').shutdownServer()" """
            # print(shutdown_with_auth1)
            # print(script)
            p2 = subprocess.Popen(shutdown_with_auth1, shell=True,
                                  stdout=subprocess.PIPE, stderr=STDOUT)
            shutdown_with_auth = f"""{MONGO} --eval "db.getSiblingDB(\'admin\').shutdownServer()" """
            # print(shutdown_with_auth)
            # print(script)
            p3 = subprocess.Popen(shutdown_with_auth, shell=True,
                                  stdout=subprocess.PIPE, stderr=STDOUT)
            r1 = p1.stdout.read().decode('utf-8')
            r2 = p2.stdout.read().decode('utf-8')
            if 'server should be down...' in r1 or 'connect failed' in r2:
                result = 'server should be down...'
            else:
                result = 'server is already down...'
        else:
            try:
                pid = Script.run('pgrep mongo')
                script = f'kill -2 {pid}'
                result = Script.run(script)
                result = 'server should be down...'
            except subprocess.CalledProcessError:
                result = 'server is already down...'

        print(result)

    def set_auth(self):
        """
        add admin account into the MongoDB admin database
        """

        mode = self.data['MODE']

        if mode == 'docker':
            Console.error("* Docker is not yet supported")
            raise NotImplementedError

        if platform.lower() == 'win32':  # don't remove this otherwise init won't work in windows, eval should start with double quote in windows
            self.data['MONGO'] = f"{self.mongo_home}\\bin\mongo"
            script = """ "{MONGO}" --eval "db.getSiblingDB('admin').createUser({{ user:'{MONGO_USERNAME}',pwd:'{MONGO_PASSWORD}',roles:[{{role:'root',db:'admin'}}]}}) ; db.shutdownServer()" """.format(
                **self.data)
            # print(script)
            try:
                # result = Shell.run2(script)
                p = subprocess.Popen(script, shell=True, stdout=subprocess.PIPE,
                                     stderr=STDOUT)
                result = p.stdout.read().decode('utf-8')
            except Exception as e:
                print(e)
                return


        else:
            script = """mongo --eval 'db.getSiblingDB("admin").createUser({{user:"{MONGO_USERNAME}",pwd:"{MONGO_PASSWORD}",roles:[{{role:"root",db:"admin"}}]}})'""".format(
                **self.data)
            result = Script.run(script)
        if "Successfully added user" in result:
            Console.ok("Administrative user created.")
        elif "already exists" in result:
            Console.error('admin user already exists.')
        else:
            Console.error("Problem creating the administrative user. Check "
                          "the yaml file and make sure the password and "
                          "username are not TBD.")
        # print(result)

    def dump(self, filename):
        """

        :param filename: The filename

        dump the entire MongoDB database into output location

        """
        #
        # TODO: BUG: expand user
        #

        mode = self.data['MODE']

        if mode == 'docker':
            Console.error("* Docker is not yet supported")
            raise NotImplementedError

        script = "mongodump --authenticationDatabase admin --archive={self.mongo_home}/{filename}.gz --gzip -u {MONGO_USERNAME} -p {MONGO_PASSWORD}".format(
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

        mode = self.data['MODE']

        if mode == 'docker':
            Console.error("* Docker is not yet supported")
            raise NotImplementedError

        script = "mongorestore --authenticationDatabase admin -u {MONGO_USERNAME} -p " \
                 "{MONGO_PASSWORD} --gzip --archive={self.mongo_home}/{filename}.gz".format(
            **self.data, filename=filename)
        result = Script.run(script)
        print(result)

    def status(self):
        """
        check the MongoDB status
        returns a json object with status: and pid: command
        """

        mode = self.data['MODE']

        if mode == 'docker':
            Console.error("* Docker is not yet supported")
            raise NotImplementedError

        if platform.lower() == 'win32':
            script = """
            tasklist /FO LIST /FI "IMAGENAME eq mongod.exe"
            """
            output = Script.run(script)
            if 'INFO: No tasks are running which match the specified criteria.' in output:
                result = None
            else:
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

        mode = self.data['MODE']

        if mode == 'docker':
            Console.error("* Docker is not yet supported")
            raise NotImplementedError

        ver = None
        try:
            out = \
                subprocess.check_output("mongod --version", encoding='UTF-8',
                                        shell=True).splitlines()[0].split(
                    "version")[
                    1].strip().split(".")
            ver = (int(out[0][1:]), int(out[1]), int(out[2]))
        except Exception as e:
            return None
        return ver

    def stats(self):

        mode = self.data['MODE']

        if mode == 'docker':
            Console.error("* Docker is not yet supported")
            raise NotImplementedError

        script = """mongo --eval 'db.stats()'""".format(**self.data)

        result = Script.run(script).splitlines()

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

    def is_installed_as_win_service(self):
        """
        returns True if mongodb is installed as a windows service
        :return:
        """
        if platform == 'win32':
            win_services = list(psutil.win_service_iter())
            mongo_service = []
            for service in win_services:
                if 'mongo' in service.display_name().lower():
                    mongo_service.append(service)
            is_service = len(mongo_service) > 0
            return is_service
        else:
            Console.error(
                f'Windows platform function called instead of {platform}')
            return False

    def win_service_is_running(self):
        """
        returns True if mongodb running
        :return:
        """
        if platform == 'win32':
            # if self.is_installed_as_win_service():
            #     win_services = list(psutil.win_service_iter())
            #     mongo_service = []
            #     for service in win_services:
            #         if 'mongo' in service.display_name().lower():
            #             mongo_service = service
            #     # mongo_service = [service for service in win_services if 'mongo' in service.display_name().lower()][0]
            #     try:
            #         return mongo_service[0].status() == 'running'
            #     except TypeError:
            #         return False
            # else:
            return "mongod.exe" in (p.name() for p in psutil.process_iter())

        else:
            Console.error(
                f'Windows platform function called instead of {platform}')
            return False

    def linux_process_is_running(self):
        """
        returns True if mongod is running
        :return:
        """
        if platform == 'linux':
            try:
                subprocess.check_output("pgrep mongo", encoding='UTF-8',
                                        shell=True)
                return True
            except subprocess.CalledProcessError as e:
                return False
        else:
            Console.error(
                f'Linux platform function called instead of {platform}')
            return False

    def mac_process_is_running(self):
        """
        returns True if mongod is running
        :return:
        """
        if platform == 'darwin':
            try:
                subprocess.check_output("pgrep mongo", encoding='UTF-8',
                                        shell=True)
                return True
            except subprocess.CalledProcessError as e:
                return False
        else:
            Console.error(
                f'Darwin platform function called instead of {platform}')
            return False

    def service_is_running(self):
        """
        checks if mongo service is running
        :return:
        """
        if platform.lower() == 'linux':
            return self.linux_process_is_running()
        elif platform.lower() == 'darwin':
            return self.mac_process_is_running()
        elif platform.lower() == 'win32':  # Replaced windows with win32
            return self.win_service_is_running()
        else:
            Console.error(f"platform {platform} not found")

    def start_if_not_running(self):
        """
        checks if mongo service is running
        :return:
        """

        mode = self.data['MODE']

        if mode == 'docker':
            Console.error("* Docker is not yet supported")
            raise NotImplementedError

        if platform.lower() == 'linux':
            if not self.linux_process_is_running():
                self.start()
        elif platform.lower() == 'darwin':
            if not self.mac_process_is_running():
                self.start()
        elif platform.lower() == 'win32':  # Replaced windows with win32
            if not self.win_service_is_running():
                self.start()
        else:
            Console.error(f"platform {platform} not found")

    def importAsFile(self, data, collection, db):

        mode = self.data['MODE']

        if mode == 'docker':
            Console.error("* Docker is not yet supported")
            raise NotImplementedError

        self.start_if_not_running()
        tmp_folder = path_expand('~/.cloudmesh/tmp')
        if not os.path.exists(tmp_folder):
            os.makedirs(tmp_folder)
        tmp_file = path_expand('~/.cloudmesh/tmp/tmp_import_file.json')
        Console.msg("Saving the data to file ")
        with open(tmp_file, 'w') as f:
            for dat in data:
                f.write(json.dumps(dat) + '\n')

        username = self.config["cloudmesh.data.mongo.MONGO_USERNAME"]
        password = self.config["cloudmesh.data.mongo.MONGO_PASSWORD"]

        cmd = f'mongoimport --db {db}' \
              f' --collection {collection} ' \
              f' --authenticationDatabase admin ' \
              f' --username {username}' \
              f' --password {password} ' \
              f' --drop' \
              f' --file {tmp_file}'

        Console.msg("Importing the saved data to database")
        result = Shell.run2(cmd)
        print(result)


"""

# TODO: develop a pytest for this

connection = pymongo.Connection(host = "127.0.0.1", port = 27017)
db = connection["test_db"]
test_collection = db["test_collection"]
db.command("dbstats") # prints database stats for "test_db"
db.command("collstats", "test_collection")
"""
