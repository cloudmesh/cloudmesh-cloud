from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from cm4.openstack.OpenstackCM import OpenstackCM
from cm4.vm.Cloud import Cloud
from cm4.configuration.config import Config
from libcloud.compute.drivers.openstack import OpenStackNodeDriver
from libcloud.compute.base import NodeDriver
import os


class Cmopenstack(Cloud):

    def __init__(self, config, cloud):
        self.driver = OpenstackCM(cloud)  # cloud is chameleon
