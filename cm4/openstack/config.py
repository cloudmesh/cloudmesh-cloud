import yaml


class Config(object):

    def __init__(self, debug=False):
        self.debug = debug
        self.path = "/Users/ruili/Dropbox/FA18-E516/cm/cm4/openstack/cloudmesh.yaml"
        self._conf = {}


    '''
    Read yaml file from default path self.path
    '''
    def config(self):
        with open(self.path, "r") as f:
            try:
                self._conf = yaml.load(f)
            except yaml.YAMLError as exc:
                print(exc)

    def get_default(self):
        '''
        ingest the default information

        :return default: the content in default block
        '''

        default = self._conf.get('cloudmesh').get('default')
        return default

    def get_cloud(self):
        '''
        ingest the cloud information

        :return cloud: the content in cloud block
        '''

        cloud = self._conf.get('cloudmesh').get('cloud')
        return cloud

    def get_cluster(self):
        '''
        ingest the cluster information

        :return cluster: the content in cluster block
        '''

        cluster = self._conf.get('cloudmesh').get('cluster')
        return cluster

    def get_config(self):
        '''
        ingest the content of yaml file

        :return conf: all information in yaml file
        '''

        return self._conf

