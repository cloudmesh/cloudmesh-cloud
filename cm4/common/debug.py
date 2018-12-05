import inspect


def HEADING(name):
    print()
    print("#", 79 * "-")
    print ("#", name)
    print ("#", 79 * "-")
    print()

myself = lambda: inspect.stack()[1][3]