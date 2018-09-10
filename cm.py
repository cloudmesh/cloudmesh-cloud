from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import yaml


class cloudmesh:

    def __init__(self):
        self._conf = {}

    def config(self, name="./cloudmesh.yaml"):
        # reads in the yaml file
        with open(name, "r") as stream:
            self._conf = yaml.load(stream)
            print(yaml.dump(self._conf))

    def get_driver(self, cloudname=None):
        # if cloudname=none get the default cloud
        # credentials = ….
        # return the driver for that cloud
        # now if you do that right you cans implify libcloud use with
        if cloudname is None:
            cloudname = self._conf.get('cloudmesh').get('default').get('cloud')

        conn = None
        if cloudname == 'azure':
            AZURE_SUBSCRIPTION_ID = self._conf.get('cloudmesh').get('cloud').get('azure').get('credentials').get(
                'AZURE_SUBSCRIPTION_ID')
            AZURE_MANAGEMENT_CERT_PATH = self._conf.get('cloudmesh').get('cloud').get('azure').get('credentials').get(
                'AZURE_MANAGEMENT_CERT_PATH')
            AZDriver = get_driver(Provider.AZURE)
            conn = AZDriver(subscription_id=AZURE_SUBSCRIPTION_ID, key_file=AZURE_MANAGEMENT_CERT_PATH)
        elif cloudname == 'aws':
            EC2_ACCESS_ID = self._conf.get('cloudmesh').get('cloud').get('aws').get('credentials').get('EC2_ACCESS_ID')
            EC2_SECRET_KEY = self._conf.get('cloudmesh').get('cloud').get('aws').get('credentials').get(
                'EC2_SECRET_KEY')
            EC2Driver = get_driver(Provider.EC2)
            conn = EC2Driver(EC2_ACCESS_ID, EC2_SECRET_KEY)

        return conn


if __name__ == '__main__':
    cm = cloudmesh()
    cm.config()
    driver = cm.get_driver("aws")
    print("driver=", driver)
    # connection = cm.get_driver("azure")
    # retrieve available images and sizes
    # images = connection.list_images()
