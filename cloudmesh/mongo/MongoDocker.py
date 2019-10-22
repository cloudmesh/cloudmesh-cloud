from cloudmesh.configuration.Config import Config
from cloudmesh.common.util import path_expand
from cloudmesh.management.script import Script, SystemPath
from cloudmesh.management.script import find_process


class MongoDocker(object):

    def __init__(self, configuration="~/.cloudmesh/cloudmesh.yaml"):
        path = path_expand(configuration)
        self.config = Config(config_path=path)
        self.data = self.config["cloudmesh.data.mongo"]

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
        raise NotImplementedError

    def create_image(self):
        """
        Creates the MongoDB Container
        :return:
        """
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
        raise NotImplementedError

    def create_admin(self):
        """
        Creates the admin user in the Container
        :return:
        """
        raise NotImplementedError

    def status(self):
        """
        Status of the the MongoDB Container
        :return: DIct with the status
        """
        raise NotImplementedError




