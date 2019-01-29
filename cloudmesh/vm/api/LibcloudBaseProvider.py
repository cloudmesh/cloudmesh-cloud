from cm4.mongo.DataBaseDecorator import DatabaseUpdate
from cloudmesh.abstractclass import ComputeNodeManagerABC
from libcloud.compute.base import NodeDriver
from cloudmesh.common.dotdict import dotdict


class LibcloudBaseProvider(ComputeNodeManagerABC):
    """
    Base class for LibCloud based providers.
    Has default calls for NodeDriver methods that
    typically don't require any different processing
    for different clouds or `ex_` methods.
    """

    def __init__(self, cloud, config):
        """
        Sets `cloud`, `credentials`, `default`, and `cm` values.
        :param cloud:
        :param config:
        """
        super().__init__(cloud, config)
        self.driver = NodeDriver("")
        self.default_image = None
        self.default_size = None
        self.public_key_path = config["profile"]["key"]["public"]

    def create(self, name=None, image=None, size=None, timeout=360, **kwargs):
        """
        creates a named node
        :return:
        """
        return self.driver.create_node(name=name,
                                       image=image or self._get_default_image(),
                                       size=image or self._get_default_size(),
                                       **kwargs)

    def nodes(self):
        """
        list all nodes id
        :return: an array of libcloud Node objects
        """
        return self.driver.list_nodes()

    def info(self, name=None):
        """
        get info for one node in the list of nodes
        :param name:
        :return:
        """
        node = next(filter(lambda n: n.name == name, self.nodes()), None)
        return node

    def suspend(self, name=None):
        return self.stop(name)

    def resume(self, name=None):
        """
        resume the named node

        :param name: the name of the node
        :return: the dict of the node
        """
        return self.start(name)

    def destroy(self, name=None):
        """
        Destroys the node
        :param name: the name of the node
        :return: the dict of the node
        """
        node = self.info(name)
        self.driver.destroy_node(node)
        return node

    @DatabaseUpdate("sizes", ComputeNodeManagerABC._map_default)
    def list_sizes(self):
        """
        list all sizes available from this provider
        :return:
        """
        return self.driver.list_sizes()

    @DatabaseUpdate("locations", ComputeNodeManagerABC._map_default)
    def list_locations(self):
        """
        list all sizes available from this provider
        :return:
        """
        return self.driver.list_locations()

    def _get_default_image(self):
        """
        Get an image object corresponding to teh default image id in config.
        :return:
        """
        if self.default_image is None:
            self.default_image = self.driver.get_image(self.default["image"])
        return self.default_image

    def _get_default_size(self):
        """
        Get an size object corresponding to teh default image id in config.
        :return:
        """
        if self.default_size is None:
            sizes = self.list_sizes()
            self.default_size = [s for s in sizes if s["id"] == self.default["size"]][0]
        return dotdict(self.default_size)

    def start(self, name):
        pass

    def stop(self, name=None):
        pass
