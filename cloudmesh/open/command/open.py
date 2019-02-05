from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand

from cloudmesh.common.console import Console
import webbrowser
from cloudmesh.common.util import path_expand
import os.path
from pprint import pprint
from pathlib import Path

class OpenCommand(PluginCommand):

    # see https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/OpenCommand.py

    # noinspection PyUnusedLocal
    @command
    def do_open(self, args, arguments):
        """
        ::

            Usage:
                open FILENAME
                open doc

            Arguments:

                FILENAME  the file to open in the cwd if . is
                          specified. If file in in cwd
                          you must specify it with ./FILENAME

                          if the FILENAME is doc than teh documentation from the Web
                          is opened.

            Description:

                Opens the given URL in a browser window.
        """

        filename = arguments.FILENAME

        if filename == "doc":
            filename = "https://cloudmesh-community.github.io/cm/"

        if not (filename.startswith("file:") or filename.startswith("http")):

            if not filename.startswith(".") and not filename.startswith("/"):
                filename = "./" + filename

            filename = path_expand(filename)

            if os.path.isfile(Path(filename)):
                filename = "file://" + filename
            else:
                Console.error(
                    "unsupported browser format in file {0}".format(filename))
                return ""

        Console.ok("open {0}".format(filename))

        try:
            webbrowser.open("%s" % filename)
        except:
            Console.error(
                "can not open browser with file {0}".format(filename))
        return ""



