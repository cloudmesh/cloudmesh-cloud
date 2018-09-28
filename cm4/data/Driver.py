#! /usr/bin/env python
########################################################################
#
#    Copyright 2018 cloudmesh.org
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#    License: Apache 2.0
#
########################################################################
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import oyaml as yaml


class Driver(object):

    def __init__(self):
        self._conf = {}

    def config(self, name="./cloudmesh.yaml"):
        # reads in the yaml file
        with open(name, "r") as stream:
            self._conf = yaml.load(stream)
            print(yaml.dump(self._conf))

    # noinspection PyPep8Naming
    def get(self, cloudname=None):
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
    cm = Driver()
    cm.config()
    driver = cm.get("aws")
    print("driver=", driver)
    # connection = cm.get_driver("azure")
    # retrieve available images and sizes
    # images = connection.list_images()
