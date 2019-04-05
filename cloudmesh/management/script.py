"""
A convenient method to execute shell commands and return their output. Note: that this method requires that the
command be completely executed before the output is returned. For many activities in cloudmesh this is sufficient.
"""
import subprocess
import textwrap
from sys import platform
from cloudmesh.common.Shell import Shell

import psutil


class SystemPath(object):
    """Managing the System path in the .bashrc or .bash_profile files"""

    @staticmethod
    def add(path):
        """
        Adds a path to the ``~/.bashrc`` or ``~/.bash_profile`` files.

        TODO: Windows is not implemented yet.

        :param path: The path to be added
        :return:
        """
        script = None
        if platform == "darwin":
            script = f"""
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
        # noinspection PyUnusedLocal
        installer = Script.run(script)


class Script(object):
    """Executing a script defined by a simple text parameter"""

    @staticmethod
    def run(script, live=False, debug=False):
        """
        run the specified script line by line.

        TODO: at one point this should be moved to cloudmesh.common


        :param script: The script
        :param debug: If true the output of the script is printed
        :return:
        """
        if script is not None:
            result = ""
            lines = textwrap.dedent(script).strip().split("\n")
            if debug:
                print("===============")
                print(lines)
                print("===============")
            for line in lines:
                if live:
                    r = Shell.live(line)
                else:
                    r = subprocess.check_output(line, encoding='UTF-8', shell=True)
                if debug:
                    print(r)
                result = result + r
            return result
        else:
            return ""




def find_process(name):
    """ find a process by name

    :param name: the name of the process
    :return: A list of dicts in which the attributes pid, command, and created are available and the name matches
             the specified name argument.

    TODO: at one point this should be moved to cloudmesh.common

    Return a list of processes matching 'name'.
    """

    processes = None
    for p in psutil.process_iter():
        found = None
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
