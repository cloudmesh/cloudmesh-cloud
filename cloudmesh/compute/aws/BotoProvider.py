# import boto3
from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.util import path_expand
from cloudmesh.common.debug import VERBOSE


class Provider(ComputeNodeABC):

    kind = "aws_boto"

    def __init__(self, name=None, configuration="~/.cloudmesh/.cloudmesh4.yaml"):
        super().__init__(name=name, configuration=configuration)

    # implement the functions from ComputeNodeABc
