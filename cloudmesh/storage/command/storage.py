from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.storage.api.manager import Manager

class StorageCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_storage(self, args, arguments):
        """
        ::

          Usage:
                starage [--service=SERVICE] put FILENAME
                starage [--service=SERVICE] get FILENAME
                starage [--service=SERVICE] delete FILENAME
                starage [--service=SERVICE] size FILENAME
                starage [--service=SERVICE] info FILENAME
                storage [--service=SERVICE] create FILENAME
                storage [--service=SERVICE] sync SOURCEDIR DESTDIR


          This command does some useful things.

          Arguments:
              FILE   a file name

          Options:
              -f      specify the file

          Example:
            set service=box
            starage  put FILENAME

            is the same as 

            starage  --service=box put FILENAME


        """
        arguments.FILE = arguments['--file'] or None

        print(arguments)

        m = Manager()


        if arguments.FILE:
            print("option a")
            m.list(arguments.FILE)

        elif arguments.list:
            print("option b")
            m.list("just calling list without parameter")




