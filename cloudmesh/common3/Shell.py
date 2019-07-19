"""
A convenient method to execute shell commands and return their output. Note: that this method requires that the
command be completely execute before the output is returned. FOr many activities in cloudmesh this is sufficient.
"""
import sys

from cloudmesh.common.Shell import Shell as Shell2
from cloudmesh.common.console import Console
import subprocess
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.debug import VERBOSE

class Shell(Shell2):

    @staticmethod
    def run(command, encoding='utf-8'):
        cmd = f"{command}; exit 0"
        r = subprocess.check_output(command,
                                    stderr=subprocess.STDOUT,
                                    shell=True)
        if encoding is None or  encoding == 'utf-8':
            return str(r, 'utf-8')
        else:
            return r

    @staticmethod
    def run_timed(label, command, encoding=None, service=None):
        _label = str(label)
        print(_label, command)
        StopWatch.start(f"{service} {_label}")
        result = Shell.run(command, encoding)
        StopWatch.stop(f"{service} {_label}")
        return str(result)

    @classmethod
    def check_python(cls):
        """
        checks if the python version is supported
        :return: True if it is supported
        """
        python_version = sys.version_info[:3]

        v_string = [str(i) for i in python_version]

        if python_version[0] == 2:
            Console.error(f"You are running an unsupported version of python: {python_version}")
            Console.error("Please update to python version 3.7")
            sys.exit(1)

        elif python_version[0] == 3:

            python_version_s = '.'.join(v_string)
            if (python_version[0] == 3) and (python_version[1] >= 7) and (python_version[2] >= 0):

                Console.ok(f"You are running a supported version of python: "
                           f"{python_version_s}")
            else:
                Console.error(
                    "WARNING: You are running an unsupported version of python: {:}".format(
                        python_version_s))
                Console.error("         We recommend you update your python")

        # pip_version = pip.__version__
        python_version, pip_version = cls.get_python()

        if int(pip_version.split(".")[0]) >= 18:
            Console.ok(f"You are running a supported version of pip: {pip_version}")
        else:
            Console.error("WARNING: You are running an old version of pip: " + str(
                pip_version))
            Console.error("         We recommend you update your pip  with \n")
            Console.error("             pip install -U pip\n")

    @staticmethod
    def ssh(name=None, user=None, key=None, command=None):

        location = ""

        if user is None:
            location = pubip
        else:
            location = user + '@' + pubip
        cmd = ['ssh',
               "-o", "StrictHostKeyChecking=no",
               "-o", "UserKnownHostsFile=/dev/null",
               '-i', key, location, command]
        VERBOSE(" ".join(cmd))

        ssh = subprocess.Popen(cmd,
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        result = ssh.stdout.readlines()
        if result == []:
            error = ssh.stderr.readlines()
            print("ERROR: %s" % error)
        else:
            print("RESULT:")
            for line in result:
                line = line.decode("utf-8")
                print(line.strip("\n"))
