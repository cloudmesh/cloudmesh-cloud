"""
A convenient method to execute shell commands and return their output. Note:
that this method requires that the command be completely executed before the
output is returned. For many activities in cloudmesh this is sufficient.
"""
import subprocess
import textwrap
from sys import platform
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console

import psutil
import os


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

        def which_shell():
            shell = os.environ["SHELL"]
            for s in ['bash', 'zsh']:
                if s in shell:
                    return s
            return shell

        def is_in_path(what):
            os_path = os.environ['PATH'].split(":")
            return what in os_path

        script = None

        if platform == "darwin":

            if is_in_path(path):
                return

            shell = which_shell()

            if shell == 'bash':
                Console.ok(f"We will be adding to the ~.bash_profile {path}")
                script = f"""
                echo \"export PATH={path}:$PATH\" >> ~/.bash_profile
                source ~/.bash_profile
                """
            elif shell == "zsh":
                Console.ok(f"We will be adding to the ~/.zprofile {path}")
                script = f"""
                echo \"export PATH={path}:$PATH\" >> ~/.zprofile
                source ~/.zprofile
                """
            else:
                script = f"""
                echo \"Shell {shell} not supported
                """
        elif platform == "linux":
            if is_in_path(path):
                return

            Console.ok(f"We will be adding to the ~.bash_profile {path}")
            script = f"""
            echo \"export PATH={path}:$PATH\" >> ~/.bashrc
            source ~/.bashrc
            """
        elif platform == "windows":
            script = None
            # TODO: BUG: Implement.
            # Current workaround functiosn as follows. We could even make this the default model,
            # e.g. take the path from cloudmesh.yaml
            # in windows we added the path to mongod and mongo from the cloudmesh.yaml file
        # noinspection PyUnusedLocal
        if script is not None:
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
            lines = textwrap.dedent(script).strip().splitlines()
            if debug:
                print("===============")
                print(lines)
                print("===============")
            for line in lines:
                if live:
                    r = Shell.live(line)
                else:
                    r = subprocess.check_output(line, encoding='UTF-8',
                                                shell=True)
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
