import platform
import sys
import os


class OperatingSystem(object):

    @staticmethod
    def get():
        d = {
            "system": platform.system(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "virtualenv": hasattr(sys, 'real_prefix'),
            "path": os.path.dirname(sys.executable),
            "pyenv": ".pyenv" in os.path.dirname(sys.executable),
        }
        return d
