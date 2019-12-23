"""
A convenient method to execute shell commands and return their output.
Note: that this method requires that the
command be completely execute before the output is returned.
For many activities in cloudmesh this is sufficient.
"""
import subprocess
import sys
from sys import platform
import ctypes

from cloudmesh.common.Shell import Shell as Shell2
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.console import Console


class Shell(Shell2):

    @staticmethod
    def run(command, encoding='utf-8'):
        """
        executes the command and returns the output as string
        :param command:
        :param encoding:
        :return:
        """
        
        if sys.platform == "win32":
            command = f"{command}"
        else:
            command = f"{command}; exit 0"
            
        r = subprocess.check_output(command,
                                    stderr=subprocess.STDOUT,
                                    shell=True)
        if encoding is None or encoding == 'utf-8':
            return str(r, 'utf-8')
        else:
            return r

    @staticmethod
    def run2(command, encoding='utf-8'):
        """
        executes the command and returns the output as string. This command also
        allows execution of 32 bit commands.

        :param command: the program or command to be executed
        :param encoding: encoding of the output
        :return:
        """
        if platform.lower() == 'win32':
            class disable_file_system_redirection:
                _disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
                _revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection

                def __enter__(self):
                    self.old_value = ctypes.c_long()
                    self.success = self._disable(ctypes.byref(self.old_value))

                def __exit__(self, type, value, traceback):
                    if self.success:
                        self._revert(self.old_value)

            with disable_file_system_redirection():
                command = f"{command}"
                r = subprocess.check_output(command,
                                            stderr=subprocess.STDOUT,
                                            shell=True)
                if encoding is None or encoding == 'utf-8':
                    return str(r, 'utf-8')
                else:
                    return r
        elif platform.lower() == 'linux' or platform.lower() == 'darwin':
            command = f"{command}"
            r = subprocess.check_output(command,
                                        stderr=subprocess.STDOUT,
                                        shell=True)
            if encoding is None or encoding == 'utf-8':
                return str(r, 'utf-8')
            else:
                return r

    @staticmethod
    def run_os_system(command, encoding='utf-8'):
        return NotImplementedError

    @staticmethod
    def cms(command, encoding='utf-8'):
        return Shell.run("cms " + command, encoding=encoding)

    @staticmethod
    def run_timed(label, command, encoding=None, service=None):
        """
        runs teh command and uses the StopWatch to time it
        :param label: name of the StopWatch
        :param command: the command to be executed
        :param encoding: the encoding
        :param service: a prefix to the stopwatch label
        :return:
        """
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
            Console.error(
                f"You are running an unsupported version "
                f"of python: {python_version}")
            Console.error("Please update to python version 3.7 or 3.8")
            sys.exit(1)

        elif python_version[0] == 3:

            python_version_s = '.'.join(v_string)
            if (python_version[0] == 3) and (python_version[1] >= 7) and \
                (python_version[2] >= 0):

                Console.ok(f"You are running a supported version of python: "
                           f"{python_version_s}")
            else:
                Console.error(
                    "WARNING: You are running an unsupported version of "
                    "python: {:}".format(python_version_s))
                Console.error("         We recommend you update your python")

        # pip_version = pip.__version__
        python_version, pip_version = cls.get_python()

        if int(pip_version.split(".")[0]) >= 18:
            Console.ok(
                f"You are running a supported version of pip: {pip_version}")
        else:
            Console.error(
                "WARNING: You are running an old version of pip: " + str(
                    pip_version))
            Console.error("         We recommend you update your pip  with \n")
            Console.error("             pip install -U pip\n")
