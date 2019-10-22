from cloudmesh.configuration.Config import Config
from cloudmesh.common.util import path_expand
from cloudmesh.management.script import Script, SystemPath
from cloudmesh.management.script import find_process
from cloudmesh.common.console import Console

class MongoDocker(object):


    def __init__(self, configuration="~/.cloudmesh/cloudmesh.yaml", dryrun=False):
        path = path_expand(configuration)
        self.config = Config(config_path=path)
        self.data = self.config["cloudmesh.data.mongo"]

        self.NAME = "cloudmesh-mongo"

        self.username = self.data["MONGO_USERNAME"]
        self.password = self.data["MONGO_PASSWORD"]
        self.port = self.data["MONGO_PORT"]
        self.host = self.data["MONGO_HOST"]
        self.dryrun = dryrun

    def run(self, script, verbose=True):
        if self.dryrun:
            if verbose:
                print (script)
            return "dryrun"
        else:
            installer = Script.run(script)
            if verbose:
                print(installer)
            return installer


    def start(self):
        """
        Starts the MongoDBd Container
        :return:
        """
        script = "docker run -d -p 127.0.0.1:27017:27017/tcp --name cloudmesh-mongo mongo"
        id = self.run(script, verbose=False)

        Console.ok("Starting docker mongo container with id")
        Console.msg("")
        Console.msg(f"   {id}")
        Console.msg("")

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


    def ps(self):
        """
        Creates the Mongo image
        :return:
        """

        #script = \
        #    f"docker build . -t {self.NAME}"

        script = \
            f"docker ps"
        self.run(script)


    def pull(self):
        """
        Creates the Mongo image
        :return:
        """

        #script = \
        #    f"docker build . -t {self.NAME}"

        script = \
            f"docker pull mongo"
        self.run(script)

    def start_mongo(self):
        """
        Creates the MongoDB Container
        :return:
        """
        script = \
            f"docker run -d -p {self.host}:{self.port}:{self.port}" \
            f" --name {self.NAME}" \
            f" -e MONGO_INITDB_ROOT_USERNAME={self.username}" \
            f" -e MONGO_INITDB_ROOT_PASSWORD={self.password}" \
            f" mongo"
        script = f"docker run -d -p {self.host}:{self.port}:{self.port}/tcp --name {self.NAME} mongo"
        self.run(script)

    def create_admin(self):
        """
        Creates the admin user in the Container
        :return:
        """
        # script = """ "{MONGO}" --eval "db.getSiblingDB('admin').createUser({{ user:'{MONGO_USERNAME}',pwd:'{MONGO_PASSWORD}',roles:[{{role:'root',db:'admin'}}]}}) ; db.shutdownServer()" """.format(**self.data)
        #

        # docker exec cloudmesh-mongo  mongo --eval "db.getSiblingDB('admin').createUser({user:'admin',pwd:'ab12',roles:[{role:'root',db:'admin'}]});"
        # docker exec cloudmesh-mongo  mongo --eval "db.getSiblingDB('admin').createUser({user:'admin',pwd:'ab12',roles:[{role:'root',db:'admin'}]});"
        script = \
          f"docker exec {self.NAME}  mongo --eval "\
          '"'\
          "db.getSiblingDB('admin').createUser({"\
          f"user:'{self.username}',"\
          f"pwd:'{self.password}',"\
          "roles:[{role:'root',db:'admin'}]});"\
          '"'
        print (script)
        self.run(script)

    def status(self):
        """
        Status of the the MongoDB Container
        :return: DIct with the status
        """
        raise NotImplementedError

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

            script = \
                f"docker stop {id}" \
                f"docker rm {id}"
            self.run(script, verbose=False)
        except:
            Console.ok("No container found.")


if __name__ == "__main__":
    mongo = MongoDocker()

    #mongo = MongoDocker(dryrun=True)
    mongo.pull()

    mongo.ps()
    mongo.kill()
    mongo.start()
    mongo.create_admin()
    #mongo.start_mongo()
    #mongo.ps()

    #mongo.stop()

"""
docker run --name cloudmesh-mongo -d -p 27017:27017 mongo 
docker exec cloudmesh-mongo ls

"""
