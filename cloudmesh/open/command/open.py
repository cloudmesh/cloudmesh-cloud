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
                open account aws [NAME]


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

                open account aws [NAME]
                    opens the aws users web page, if the NAME is users or is
                    omitted, it goes to the page that allows you to create a user

        """

        # pprint(arguments)
        filename = arguments.FILENAME

        if arguments.aws and arguments.account:
            name = arguments.NAME or "users"

            if name == "users":
                filename = f"https://console.aws.amazon.com/iam/home#/users"
            else:
                filename = "https://console.aws.amazon.com/iam/home#/users" \
                           f"/{name}?section=security_credentials"
        elif arguments.baremetal and arguments.tacc:
            filename = str("https://chi.tacc.chameleoncloud.org")
        elif arguments.baremetal and arguments.uc:
            filename = str("https://chi.uc.chameleoncloud.org")
        elif arguments.chameleon and (arguments.vm or arguments.openstack):
            filename = str("https://openstack.tacc.chameleoncloud.org")

        elif arguments.doc and arguments.local:
            filename = "./docs/index.html"

        elif filename == "doc":
            # filename = "https://cloudmesh-community.github.io/"
            filename = "https://cloudmesh.github.io/cloudmesh-manual/"

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
