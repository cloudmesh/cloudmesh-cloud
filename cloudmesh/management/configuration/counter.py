from __future__ import print_function
from os.path import isfile, expanduser, join, dirname, realpath, exists
from os import mkdir
from shutil import copyfile
from pathlib import Path
import oyaml as yaml


class Counter(object):
    """
    A counter is used to keep track of some value that can be increased
    and is associated with a user. Typically it is used to increment the
    vm id or the job id.
    """

    __shared_state = {}

    def __init__(self, counter_file_path="~/.cloudmesh/counter.yaml"):
        """
        :param counter_file_path: the counter is always stored in this file.
               There can be counters with different names in the file.
        """
        self.counters = {}
        self.counter_file_path = expanduser(counter_file_path)
        config_folder = dirname(self.counter_file_path)

        if not exists(config_folder):
            mkdir(config_folder)

        if not isfile(self.counter_file_path):
            destination_path = Path(join(dirname(realpath(__file__)), "../etc/counter.yaml"))
            copyfile(destination_path.resolve(), self.counter_file_path)

        with open(self.counter_file_path, "r") as stream:
            self.counters = yaml.load(stream, Loader=yaml.FullLoader)

    def incr(self, name='counter'):
        """
        increments the counter by one
        :return:
        """
        counter_value = self.counters.get(name)
        if counter_value is not None:
            self.set(name,  counter_value + 1)
        else:
            raise AttributeError("Counters does not contain a counter with the name: " + name)

    def decr(self, name='counter'):
        """
        increments the counter by one
        :return:
        """
        counter_value = self.counters.get(name)
        if counter_value is not None:
            # make sure the counter doesn't go below 0
            counter_value = 0 if counter_value <= 1 else counter_value - 1
            self.set(name, counter_value)
        else:
            raise AttributeError("Counters does not contain a counter with the name: " + name)

    def get(self, name='counter'):
        """
        returns the value of the counter
        :param name: name of the counter
        :return: the value of the counter
        """
        return self.counters.get(name)

    def set(self, name='counter', value=None):
        """
        sets a counter associated with a particular user
        :param name: name of the counter
        :param value: the value
        :return:
        """
        # checking if the value is an int
        if isinstance(value, int):
            self.counters.__setitem__(name, value)
            with open(self.counter_file_path, "w") as stream:
                yaml.safe_dump(self.counters.copy(), stream, default_flow_style=False)
        elif value is None:
            raise ValueError("The value for the counter cannot be empty")
        else:
            raise ValueError("The value for the counter must be of type int")
