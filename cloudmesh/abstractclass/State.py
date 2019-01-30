from cloudmesh.common.dotdict import dotdict
import json


class State(dotdict):

    def __init__(self, name=None):
        self.__dict__["name"] = name
        self.__dict__["state"] = None
        self.__dict__["output"] = None

    def __str__(self):
        json.dumps(
            self.__dict__,
            sort_keys=True,
            indent=4)
