from cloudmesh.shell.variables import Variables
from cloudmesh.common.util import banner
from pprint import pformat
from pprint import pprint
import inspect

def VERBOSE(msg, verbose=9, label=None, color="BLUE"):

    if label is None:
        label = inspect.stack()[1][4][0].strip().replace("VERBOSE(", "")
        label = label.split(",")[0][:-1]

    _verbose = int(Variables()["verbose"] or 0)
    if _verbose >= verbose:
        banner(pformat(msg), label=label, color=color)
