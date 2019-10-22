from cloudmesh.configuration.Config import Config
from cloudmesh.common.util import path_expand
from cloudmesh.management.script import Script, SystemPath
from cloudmesh.management.script import find_process


class MongoDocker(object):


    def __init__(self, configuration="~/.cloudmesh/cloudmesh.yaml"):
        path = path_expand(configuration)
        self.config = Config(config_path=path)
        self.data = self.config["cloudmesh.data.mongo"]

        self.NAME = "cloudmesh-mongo"

        self.username = self.data["MONGO_USERNAME"]
        self.password = self.data["MONGO_PASSWORD"]
        self.port = self.data["MONGO_PORT"]
        self.host = self.data["MONGO_HOST"]


    def start(self):
        """
        Starts the MongoDBd Container
        :return:
        """
        raise NotImplementedError

    def stop(self):
        """
        Stops the MongoDBd Container
        :return:
        """
        try:
            script = \
                f"docker stop {self.NAME}"
            installer = Script.run(script)
            print(installer)
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

        installer = Script.run(script)
        print(installer)


    def pull(self):
        """
        Creates the Mongo image
        :return:
        """

        #script = \
        #    f"docker build . -t {self.NAME}"

        script = \
            f"docker pull mongo"



        installer = Script.run(script)
        print(installer)

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
        installer = Script.run(script)
        print(installer)

    def create_admin(self):
        """
        Creates the admin user in the Container
        :return:
        """
        # script = """ "{MONGO}" --eval "db.getSiblingDB('admin').createUser({{ user:'{MONGO_USERNAME}',pwd:'{MONGO_PASSWORD}',roles:[{{role:'root',db:'admin'}}]}}) ; db.shutdownServer()" """.format(**self.data)
        #
        script = \
          f"docker run --name {self.NAME}  mongo --eval "\
          "db.getSiblingDB('admin').createUser({"\
          f"user:'{self.username}',"\
          f"pwd:'{self.password}',"\
          "roles:[{role:'root',db:'admin'\}]\});"\
          "db.shutdownServer()"
        installer = Script.run(script)
        print(installer)

    def status(self):
        """
        Status of the the MongoDB Container
        :return: DIct with the status
        """
        raise NotImplementedError


if __name__ == "__main__":
    mongo = MongoDocker()

    mongo.ps()
    mongo.pull()
    #mongo.create_admin()
    mongo.start_mongo()
    mongo.ps()

    mongo.stop()

