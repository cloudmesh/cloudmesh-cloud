from libcloud.compute.types import Provider
from cm4.configuration.config import Config
from cm4.vm import Cmaws, Cmazure, Cmopenstack
from cm4.cmmongo.mongoDB import MongoDB


class Provider (object):

    def __init__(self):
        self.config = Config()


    # only developed for AZURE, AWS, Chameleon
    def get_provider(self, cloud):
        """
        Create the driver based on the 'kind' information.
        This method could deal with AWS, AZURE, and OPENSTACK for CLOUD block of YAML file.
        But we haven't test OPENSTACK
        :return: the driver based on the 'kind' information
        """
        os_config = self.config.get('cloud.%s' % cloud)
        if os_config.get('cm.kind') == 'azure':
            driver = Cmazure(self.os_config)
        elif os_config.get('cm.kind') == 'aws':
            driver = Cmaws(self.os_config)
        elif os_config.get('cm.kind') == 'openstack':
            driver = Cmopenstack(self.os_config)

        return driver

    '''
    def get_new_node_setting(self):
        """
        get the new node setting
        :return: the new node setting information
        """
        return self.setting
    '''


class Vm(object):

    def __init__(self, cloud):
        self.provider = Provider().get_provider(cloud)
        self.mongo = MongoDB('luoyu', 'luoyu', 27017)


    def start(self, node_id):
        """
        start the node based on the id
        :param node_id:
        :return: True/False
        """
        if self.mongo.find_document('cloud', 'id', node_id)['state'] == 'stopped':
            result = self.provider.ex_start_node(self.info(node_id))
            info = self.provider.info(node_id)
            self.mongo.update_document('cloud', 'id', node_id, info)
            return result
        else:
            return True

    def stop(self, node_id):
        """
        stop the node based on the ide
        :param node_id:
        :return: True/False
        """

        if self.mongo.find_document('cloud', 'id', node_id)['state'] == 'running':
            result = self.provider.ex_stop_node(self.info(node_id))
            self.mongo.update_document('cloud', 'id', node_id, {'state' : 'stopped'})
            return result
        else:
            return True

        return result

    def resume(self, node_id):
        """
        start the node based on id
        :param node_id:
        """
        return self.start(node_id)

    def suspend(self, node_id):
        """
        stop the node based on id
        :param node_id:
        """
        return self.stop(node_id)

    def destroy(self, node_id):
        """
        delete the node based on id
        :param node_id:
        :return: True/False
        """

        result = self.provider.destroy_node(self.info(node_id))
        self.mongo.delete_document('cloud', node_id)

        return result

    '''
    def create(self, name):
        """
        create a new node
        :param name: the name for the new node
        :return:
        """
        return self.provider.create_node(name=name, **self.provider.get_new_node_setting())
    '''

    def list(self):
        """
        list existed nodes
        :return: all nodes' information
        """
        result = self.provider.list_nodes()
        return result

    def status(self, node_id):
        """
        show node information based on id
        :param node_id:
        :return: all information about one node
        """
        status = self.info(node_id).state
        self.mongo.update_document('cloud', 'id', node_id, {'state' : status})
        return status

    def info(self, node_id):
        """
        show node information based on id
        :param node_id:
        :return: all information about one node
        """
        nodes = self.list()
        for i in nodes:
            if i.id == node_id:
                self.mongo.update_document('cloud', 'id', node_id, i)
                return i
