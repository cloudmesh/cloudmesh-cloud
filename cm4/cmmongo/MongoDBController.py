import os
import subprocess
import yaml
from sys import platform
from pymongo import MongoClient
from cm4.configuration.config import Config
from pprint import pprint
import textwrap
from cm4.common.shell import Script
from cm4.common.shell import Shell, Brew
from cm4.common.shell import SystemPath

class MongoDBController(object):

    def __init__(self):

        self.config = Config()
        self.data = self.config["cloudmesh"]["data"]["mongo"]

    def __str__(self):
        return yaml.dump(self.data, default_flow_style=False, indent=2)

    def install(self):
        """
        check where the MongoDB is installed in cmmongo location.
        if MongoDB is not installed, python help install it
        """
        path = self.data["MONGO_PATH"]
        if not os.path.isdir(path) and self.data["MONGO_AUTOINSTALL"]:
            print("MongoDB is not installed in {MONGO_PATH}".format(**self.data))
            #
            # ask if you like to install and give infor wher it is being installed
            #
            # use cloudmesh yes no question see cloudmesh 3
            #
            print("Auto-install the MongoDB into {MONGOP_PATH}".format(self.data))

            self.data["MONGO_CODE"] = self.data["MONGO_DOWNLAOD"][platform]

            if platform == 'linux':
                self.install_linux()
            if platform == 'darwin':
                self.install_darwin()
            if platform == 'windows':
                # TODO
                raise NotImplementedError

    def install_linux(self):
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
        tar -zxvf /tmp/mongodb.tgz -C {LOCAL}
        """
        installer = Script(script)
        SystemPath.add("{MONGO_HOME}/bin".format(**self.data))

        # THIS IS BROKEN AS ITS A SUPBROCESS? '. ~/.bashrc'

        # initial mongodb config file
        self.initial_mongo_config(False)

    def install_darwin(self, brew=False):
        """
        install MongoDB in Darwin system (Mac)
        """


        if brew:
            Brew.install("mongodb")
            path = Shell.which("mongod")
            SystemPath.add("{path}".format(path=path))

        else:
            script = """
            mkdir -p {MONGO_PATH}
            mkdir -p {MONGO_HOME}
            mkdir -p {MONGO_LOG}
            curl -O {MONGO_CODE} -o /tmp/mongodb.tgz
            tar -zxvf /tmp/mongodb.tgz -C {LOCAL}
            """
            installer = Script(script)
            SystemPath.add("{MONGO_HOME}/bin".format(**self.data))

            # THIS IS BROKEN AS ITS A SUPBROCESS? '. ~/.bashrc'

            # initial mongodb config file
            self.initial_mongo_config(False)

    def update_auth(self):
        """
        create admin acount in MongoDB
        """
        #
        # TODO: BUG: should that not be done differently, e.g. from commandline or via ENV variables
        #
        # run mongodb
        self.run_mongodb()

        # set up auth information
        self.set_auth()

        # shut down mongodb
        self.shutdown_mongodb()

        # enable secutiry
        self.initial_mongo_config(True)
        print("Enable the Secutiry. You will use your username and password to login the MongoDB")

    def initial_mongo_config(self, security=False):
        """
        create the MongoDB config file
        :param security: enable the security
        """
        #
        # TODO: BUG: we do not use mongoconfig, but pass everything from commandline,
        #  everything shoudl be specified in cloudmesh4.yaml
        #
        default_config_file = dict(net=dict(bindIp=self.host, port=self.port),
                                   storage=dict(dbPath=os.path.join(self.mongo_db_path, 'database'),
                                                journal=dict(enabled=True)),
                                   systemLog=dict(destination='file',
                                                  path=os.path.join(self.mongo_db_path, 'log', 'mongod.log'),
                                                  logAppend=True)
                                   )

        if security:
            default_config_file.update(dict(security=dict(authorization='enabled')))

        with open(os.path.join(self.mongo_db_path, 'mongod.conf'), "w") as output:
            try:
                yaml.dump(default_config_file, output, default_flow_style=False)
            except yaml.YAMLError as exc:
                print(exc)

    def run_mongodb(self):
        """
        start the MongoDB server
        """
        cmd = 'mongod --dbpath %s --config %s' % (
            os.path.join(self.mongo_db_path, 'database'), os.path.join(self.mongo_db_path, 'mongod.conf'))
        subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        print('MonogDB is running')

    # noinspection PyMethodMayBeStatic
    def shutdown_mongodb(self):
        """
        shutdown the MongoDB server
        linux and darwin have different way to shutdown the server, the common way is kill
        """
        cmd = 'pgrep mongo'
        pid = int(str(subprocess.check_output(cmd, shell=True).decode("utf-8")).split('\n')[0])
        cmd = 'kill %s' % pid
        subprocess.check_output(cmd, shell=True)
        print('MonogDB is stopped')

    def set_auth(self):
        """
        add admin acount into the MongoDB admin database
        """
        client = MongoClient(self.host, self.port)
        client.admin.add_user(self.username, self.password,
                              roles=[{'role': "userAdminAnyDatabase", 'db': "admin"}, "readWriteAnyDatabase"])
        client.close()

    def dump(self, output_location):
        """
        dump the entire MongoDB database into output location
        :param output_location: the location to save the backup
        """
        #
        # TODO: BUG: expand user
        #
        cmd = 'mongodump --host %s --port %s --username %s --password %s --out %s' % (self.host,
                                                                                      self.port,
                                                                                      self.username,
                                                                                      self.password,
                                                                                      output_location)
        subprocess.check_output(cmd, shell=True)

    def restore(self, data):
        """
        restore the backup data generated by dump
        :param data: the backup data folder
        """
        #
        # TODO: BUG: expand user
        #

        cmd = 'mongorestore --host %s --port %s --username %s --password %s %s' % (self.host,
                                                                                   self.port,
                                                                                   self.username,
                                                                                   self.password,
                                                                                   data)
        subprocess.check_output(cmd, shell=True)

    def status(self):
        """
        check the MongoDB status
        """
        client = MongoClient(self.host, self.port)
        pprint(client.server_info())


def main():
    test = MongoDBController()
    # test.set_auth()
    # test.check_mongo_dir_and_install()
    # test.install_mongo_darwin()
    # test.update_auth()
    # test.run_mongodb()
    # test.shutdown_mongodb()
    test.status()
    # test.dump('~/.cloudmesh/demo/version1/cm/cm4/cmmongo/MongoDB/backup')
    # test.restore ('~/.coudmesh/demo/version1/cm/cm4/cmmongo/MongoDB/backup')


if __name__ == "__main__":
    main()
