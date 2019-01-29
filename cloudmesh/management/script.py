"""
A convenient method to execute shell commands and return their output. Note: that this method requires that the
command be completely execute before the output is returned. FOr many activities in cloudmesh this is sufficient.
"""
import errno
import glob
import os
import subprocess
import sys
import zipfile

from typing import Union
from pipes import quote
from sys import platform

from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from distutils.spawn import find_executable
import textwrap
from sys import platform
import os
import psutil

class SystemPath(object):

    @staticmethod
    def add(path):
        if platform == "darwin":
            script = """
            echo \"export PATH={path}:$PATH\" >> ~/.bash_profile
            source ~/.bash_profile
            """.format(path=path)
        elif platform == "linux":
            script = """
            echo \"export PATH={path}:$PATH\" >> ~/.bashrc
            source ~/.bashrc
            """.format(path=path)
        elif platform == "windows":
            script = None
            # TODO: BUG: Implement
        installer = Script.run(script)


class Script(object):

    @staticmethod
    def run(script, debug=False):
        if script is not None:
            result = ""
            lines = textwrap.dedent(script).strip().split("\n")
            if debug:
                print("===============")
                print(lines)
                print("===============")
            for line in lines:
                r = subprocess.check_output(line, encoding='UTF-8', shell=True)
                if debug:
                    print(r)
                result = result + r
            return result
        else:
            return ""



def find_process(name):
    "Return a list of processes matching 'name'."
    processes = None
    for p in psutil.process_iter():
        try:
            found = p.name()
        except (psutil.AccessDenied, psutil.ZombieProcess):
            pass
        except psutil.NoSuchProcess:
            continue
        if name == found:
            if processes is None:
                processes = []
            processes.append(
                {
                    "pid": p.pid,
                    "command": " ".join(p.cmdline()),
                    "created": p.create_time()
            })
    return processes