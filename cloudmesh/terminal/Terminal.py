from cloudmesh.shell.variables import Variables
from cloudmesh.common.util import banner
from pprint import pformat


class VERBOSE(object):

    @staticmethod
    def print(msg, verbose=0, label=None, color="BLUE"):
        _verbose = int(Variables()["verbose"] or 0)
        if _verbose >= verbose:
            banner(pformat(msg), label=label, color=color)
