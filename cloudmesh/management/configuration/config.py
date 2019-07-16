from os import mkdir
from os.path import isfile, join, dirname, realpath, exists
from pathlib import Path
from shutil import copyfile
# from cloudmesh.DEBUG import VERBOSE
from cloudmesh.common.util import path_expand
import munch
import re
import oyaml as yaml
import sys
import shutil

from cloudmesh.common.util import backup_name
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.variables import Variables
from cloudmesh.common.console import Console
from pprint import pprint
from cloudmesh.common.FlatDict import flatten
import oyaml as yaml
from cloudmesh.common.util import banner
from cloudmesh.common.variables import Variables

# see also https://github.com/cloudmesh/client/blob/master/cloudmesh_client/cloud/register.py

class Active(object):

    def __init__(self, config_path='~/.cloudmesh/cloudmesh4.yaml'):
        self.config = Config(config_path=config_path)


    def clouds(self):
        names = []
        entries = self.config["cloudmesh"]["cloud"]
        for entry in entries:
            if entries[entry]["cm"]["active"]:
                names.append(entry)
        if len(names) == 0:
            names = None
        return names


class Config(object):
    __shared_state = {}

    def create(self, config_path='~/.cloudmesh/cloudmesh4.yaml'):
        """
        creates the cloudmesh4.yaml file in the specified location. The default is

            ~/.cloudmesh/cloudmesh4.yaml

        If the file does not exist, it is initialized with a default. You still
        need to edit the file.

        :param config_path:  The yaml file to create
        :type config_path: string
        """
        self.config_path = Path(path_expand(config_path)).resolve()
        self.config_folder = dirname(self.config_path)

        if not exists(self.config_folder):
            mkdir(self.config_folder)

        if not isfile(self.config_path):
            source = Path(join(dirname(realpath(__file__)),
                               "../../etc/cloudmesh4.yaml"))

            copyfile(source.resolve(), self.config_path)

            # read defaults
            self.__init__()

            defaults = self["cloudmesh.default"]

            #pprint(defaults)

            d = Variables()
            if defaults is not None:
                print(f"# Set default from yaml file:")

            for key in defaults:
                value = defaults[key]
                print (f"set {key}={value}")
                d[key] = defaults[key]

    @staticmethod
    def check_for_tabs(filename, verbose=True):
        """identifies if the file contains tabs and returns True if it
        does. It also prints the location of the lines and columns. If
        verbose is set to False, the location is not printed.

        :param verbose: if true prints issues
        :param filename: the filename
        :type filename: str
        :rtype: True if there are tabs in the file
        """
        filename = path_expand(filename)
        file_contains_tabs = False

        with open(filename, 'r') as f:
            lines = f.read().split("\n")

        line_no = 1
        for line in lines:
            if "\t" in line:
                file_contains_tabs = True
                location = [
                    i for i in range(len(line)) if line.startswith('\t', i)]
                if verbose:
                    Console.error(f"Tab found in line {line_no} "
                                  f"and column(s) {location}")
            line_no += 1
        return file_contains_tabs

    def __init__(self, config_path='~/.cloudmesh/cloudmesh4.yaml',
                 encrypted=False):
        """
        Initialize the Config class.

        :param config_path: A local file path to cloudmesh yaml config
            with a root element `cloudmesh`. Default: `~/.cloudmesh/cloudmesh4.yaml`
        """

        self.__dict__ = self.__shared_state
        if "data" not in self.__dict__:
            self.load(config_path=config_path)
            try:
                self.user = self["cloudmesh.profile.user"]
            except:
                pass

    def load(self, config_path='~/.cloudmesh/cloudmesh4.yaml'):
        """
        loads a configuration file
        :param path:
        :type path:
        :return:
        :rtype:
        """

        # VERBOSE("Load config")

        self.config_path = Path(path_expand(config_path)).resolve()
        self.config_folder = dirname(self.config_path)

        self.create(config_path=config_path)

        with open(self.config_path, "r") as stream:
            content = stream.read()
            content = path_expand(content)
            content = self.spec_replace(content)
            self.data = yaml.load(content, Loader=yaml.SafeLoader)

        # self.data is loaded as nested OrderedDict, can not use set or get
        # methods directly

        if self.data is None:
            raise EnvironmentError(
                "Failed to load configuration file cloudmesh4.yaml, "
                "please check the path and file locally")

        #
        # populate default variables
        #

        self.variable_database = Variables(filename="~/.cloudmesh/var-data")
        self.set_debug_defaults()

        default = self.default()

        for name in self.default():
            if name not in self.variable_database:
                self.variable_database[name] = default[name]
        if "cloud" in default:
            self.cloud = default["cloud"]
        else:
            self.cloud = None

    def save(self, path="~/.cloudmesh/cloudmesh4.yaml", backup=True):
        """
        #
        # not tested
        #
        saves th dic into the file. It also creates a backup if set to true The
        backup filename  appends a .bak.NO where number is a number that is not
        yet used in the backup directory.

        :param path:
        :type path:
        :return:
        :rtype:
        """
        path = path_expand(path)
        if backup:
            destination = backup_name(path)
            shutil.copyfile(path, destination)
        yaml_file = self.data.copy()
        with open(self.config_path, "w") as stream:
            yaml.safe_dump(yaml_file, stream, default_flow_style=False)

    def spec_replace(self, spec):

        variables = re.findall(r"\{\w.+\}", spec)

        for i in range(0, len(variables)):
            data = yaml.load(spec, Loader=yaml.SafeLoader)

            m = munch.DefaultMunch.fromDict(data)

            for variable in variables:
                text = variable
                variable = variable[1:-1]
                value = eval(f"m.{variable}")
                if "{" not in value:
                    spec = spec.replace(text, value)
        return spec

    def credentials(self, kind, name):
        """

        :param kind: the first level of attributes after cloudmesh
        :param name: the name of the resource
        :return:
        """
        return self.data["cloudmesh"][kind][name]["credentials"]

    def check_for_TBD(self, kind, name):

        configuration = Config()[f"cloudmesh.{kind}.{name}"]

        result = {"cloudmesh": {"cloud": {name: configuration}}}

        banner(f"checking cloudmesh.{kind}.{name} in ~/.cloudmesh/cloudmesh4.yaml file")

        print (yaml.dump(result))

        flat = flatten(configuration, sep=".")

        for attribute in flat:
            if "TBD" in str(flat[attribute]):
                Console.error(f"~/.cloudmesh4.yaml: Attribute cloudmesh.{name}.{attribute} contains TBD")


    def set_debug_defaults(self):
        for name in ["trace", "debug"]:
            if name not in self.variable_database:
                self.variable_database[name] = str(False)

    def dict(self):
        return self.data

    def __str__(self):
        return yaml.dump(self.data, default_flow_style=False, indent=2)

    def get(self, key, default=None):
        """
        A helper function for reading values from the config without
        a chain of `get()` calls.

        Usage:
            mongo_conn = conf.get('db.mongo.MONGO_CONNECTION_STRING')
            default_db = conf.get('default.db')
            az_credentials = conf.get('data.service.azure.credentials')

        :param default:
        :param key: A string representing the value's path in the config.
        """
        try:
            return self.data.get(key, default)
        except KeyError:
            path = self.config_path
            Console.error(f"The key '{key}' couold not be found in the yaml file '{path}'")
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)

    def __setitem__(self, key, value):
        self.set(key, value)

    def set(self, key, value):
        """
        A helper function for setting the deafult cloud in the config without
        a chain of `set()` calls.

        Usage:
            mongo_conn = conf.set('db.mongo.MONGO_CONNECTION_STRING', "https://localhost:3232")

        :param key: A string representing the value's path in the config.
        :param value: value to be set.
        """

        try:
            if "." in key:
                keys = key.split(".")
                #
                # create parents
                #
                parents = keys[:-1]
                location = self.data
                for parent in parents:
                    if parent not in location:
                        location[parent] = {}
                    location = location[parent]
                #
                # create entry
                #
                location[keys[len(keys) - 1]] = value
            else:
                self.data[key] = value

        except KeyError:
            path = self.config_path
            Console.error(
                f"The key '{key}' couold not be found in the yaml file '{path}'")
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)

        yaml_file = self.data.copy()
        with open(self.config_path, "w") as stream:
            yaml.safe_dump(yaml_file, stream, default_flow_style=False)

    def set_cloud(self, key, value):
        """
        A helper function for setting the deafult cloud in the config without
        a chain of `set()` calls.

        Usage:
            mongo_conn = conf.get('db.mongo.MONGO_CONNECTION_STRING', "https://localhost:3232")

        :param key: A string representing the value's path in the config.
        :param value: value to be set.
        """
        self.data['cloudmesh']['default']['cloud'] = value
        print("Setting env parameter cloud to: " + self.data['cloudmesh']['default']['cloud'])

        yaml_file = self.data.copy()
        with open(self.config_path, "w") as stream:
            print("Writing update to cloudmesh.yaml")
            yaml.safe_dump(yaml_file, stream, default_flow_style=False)

    def default(self):
        return dotdict(self.data["cloudmesh"]["default"])

    def __getitem__(self, item):
        """
        gets an item form the dict. The key is . separated
        use it as follows get("a.b.c")
        :param item:
        :type item:
        :return:
        """
        try:
            if "." in item:
                keys = item.split(".")
            else:
                return self.data[item]
            element = self.data[keys[0]]
            for key in keys[1:]:
                element = element[key]
        except KeyError:
            path = self.config_path
            Console.error(f"The key '{item}' couold not be found in the yaml file '{path}'")
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)
        return element

    def __delitem__(self, item):
        """
        #
        # BUG THIS DOES NOT WORK
        #
        gets an item form the dict. The key is . separated
        use it as follows get("a.b.c")
        :param item:
        :type item:
        :return:
        """
        try:
            if "." in item:
                keys = item.split(".")
            else:
                return self.data[item]
            element = self.data
            print(keys)
            for key in keys:
                element = element[key]
            del element
        except KeyError:
            path = self.config_path
            Console.error(f"The key '{item}' couold not be found in the yaml file '{path}'")
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)

    def edit(self, attribute):
        """
        edits the dict specified by the attribute and filles out all TBD values.
        :param attribute:
        :type attribute: string
        :return:
        """

        Console.ok(f"Filling out: {attribute}")

        try:
            config = Config()
            values = config[attribute]

            print(f"Editing the values for {attribute}")

            print ("Current Values:")

            print (yaml.dump(values, indent=2))

            for key in values:

                if values[key] == "TBD":
                    result = input(f"Please enter new value for {key}: ")
                    values[key] = result

            config.save()
        except Exception as e:
            print(e)
            Console.error(f"could not find the attribute '{attribute}' in the yaml file.")

