from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
from cloudmesh.common.debug import VERBOSE
from pprint import pprint


class Secgroup(object):

    def __init__(self):
        pass

    @DatabaseUpdate()
    def add (self, group, rule,  fromport, toport, protocol, cidr):
        data = {
            "cm": {
                "kind": "secgroup",
                "cloud": "secgroup",
                "name": f"{group}-{rule}",
            },
            "rule": rule,
            "fromport": fromport,
            "toport": toport,
            "protocol": protocol,
            "cdir": cidr
        }
        return data


