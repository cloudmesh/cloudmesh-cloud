from cloudmesh.configuration.Config import Config
from cloudmesh.common.util import path_expand

class MongoDocker(object):

    def __init__(self, configuration="~/.cloudmesh/cloudmesh.yaml"):
        path = path_expand(configuration)
        self.config = Config(config_path=path)

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




