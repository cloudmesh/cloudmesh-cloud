from __future__ import print_function

import os.path
import webbrowser
from pathlib import Path

from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command


class OpenCommand(PluginCommand):

    # see https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/OpenCommand.py

    # noinspection PyUnusedLocal,PyBroadException
    @command
    def do_open(self, args, arguments):
        """
        ::

            Usage:
                open chameleon baremetal tacc
                open chameleon baremetal uc
                open chameleon vm
                open chameleon openstack
                open FILENAME
                open doc local
                open doc


            Arguments:

                FILENAME  the file to open in the cwd if . is
                          specified. If file in in cwd
                          you must specify it with ./FILENAME

                          if the FILENAME is doc than teh documentation from the Web
                          is opened.

            Description:

                Opens the given URL in a browser window.

                open chameleon baremetal tacc
                   starts horizon for baremetal for chameleon cloud at TACC

                open chameleon baremetal uc
                    starts horizon for baremetal for chameleon cloud at UC

                open chameleon vm
                    starts horizon for virtual machines

        """

        # pprint(arguments)
        filename = arguments.FILENAME

        if arguments.baremetal and arguments.tacc:
            filename = str("https://chi.tacc.chameleoncloud.org")
        elif arguments.baremetal and arguments.uc:
            filename = str("https://chi.uc.chameleoncloud.org")
        elif arguments.chameleon and (arguments.vm or arguments.openstack):
            filename = str("https://openstack.tacc.chameleoncloud.org")

        elif arguments.doc and arguments.local:
            filename = "./docs/index.html"

        elif filename == "doc":
            filename = "https://cloudmesh-community.github.io/cm/"

        if not (filename.startswith("file:") or filename.startswith("http")):

            if not filename.startswith(".") and not filename.startswith("/"):
                filename = "./" + filename

            filename = path_expand(filename)

            if os.path.isfile(Path(filename)):
                filename = "file://" + filename
            else:
                Console.error(
                    "can not find the file {0}".format(filename))
                return ""

        Console.ok("open {0}".format(filename))

        try:
            webbrowser.open("%s" % filename)
        except Exception as e:
            Console.error(
                "can not open browser with file {0}".format(filename))
        return ""
