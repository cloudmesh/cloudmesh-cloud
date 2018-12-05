import inspect


# noinspection PyPep8Naming
def HEADING(name):
    print()
    print("#", 79 * "-")
    print("#", name)
    print("#", 79 * "-")
    print()


# noinspection PyPep8
myself = lambda: inspect.stack()[1][3]
