from __future__ import print_function

from cloudmesh.common.console import Console
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command


class UrlCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_url(self, args, arguments):
        """
        ::

          Usage:
                url URL [--format=json|yaml|txt]

          This command does some useful things.

          Arguments:
              URL      The url

          Options:
              -f      specify the file

          Description:

             url http://localhost:8080

               downloads the content of the specified url and displays it

             url http://localhost:8080 --format=json

               downloads the content of the specified url and displays it in
               a pretty json format

        """

        print(arguments)

        """.j
        see: http://docs.python-requests.org/en/master/
        
        r = requests.get(arguments.URL)
        >>> r.status_code
        200
        >>> r.headers['content-type']
        'application/json; charset=utf8'
        >>> r.encoding
        'utf-8'
        >>> r.text
        u'{"type":"User"...'
        >>> rson()
        """

        Console.error("Implement me")
        return ""
