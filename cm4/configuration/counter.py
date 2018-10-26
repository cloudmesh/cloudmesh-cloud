from __future__ import print_function

class Counter(object):
    """
    A counter is used to keep track of some value that can be increased
    and is associated with a user. Typically it is used to increment the
    vm id or the job id.
    """

    def __init__(self, name="counter", filename="~/.cloudmesh/counter.yaml"):
        """
        :param name: name of the counter
        :param user: username associated with the counter
        :param filename: the counter is always stored in this file.
               There can be counters with different names in the file.
        """

    def incr(cls, name='counter'):
        """
        increments the counter by one
        :return:
        """
        raise NotImplementedError()

    def get(cls, name='counter'):
        """
        returns the value of the counter
        :param name: name of the counter
        :return: the value of the counter
        """
        raise NotImplementedError()

    def set(cls, name='counter', value=None):
        """
        sets a counter associated with a particular user
        :param name: name of the counter
        :param value: the value
        :return:
        """
        # test if value is an int
        # than set
        raise NotImplementedError()
