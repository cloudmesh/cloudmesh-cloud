import cm4.command.command
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand


def with_cm4_doc(func):
    """
    Sets the docstring from cm4.command.command so that
    it does not need to be copied.
    :param func: the function for the decorator
    """
    def new(instance, args, arguments):
        func(instance, args, arguments)

    new.__doc__ = cm4.command.command.__doc__
    return new


class Cm4Command(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    @with_cm4_doc
    def do_cm4(self, args, arguments):
        cm4.command.command.process_arguments(arguments)

