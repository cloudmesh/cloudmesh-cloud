from cloudmesh.configuration.Config import Config
from textwrap import dedent
import oyaml as yaml
from cloudmesh.common.console import Console
import sys

class Entry:
    """
    add an entry to the yaml file.

    entry_text = '''
    cloudmesh:
      sample:
        cm:
          name:
        credential:
          value:
    '''

    entry = Entry.add(entry=entry_text, path="~/.cloudmesh/cloudmesh.yaml, )

    """

    @staticmethod
    def add(entry=None, path="~/.cloudmesh/cloudmesh.yaml", ):

        try:
            _entry = dedent(entry)
            data = yaml.safe_load(_entry)

            # verify format
            # cloudmesh.entry contains "cm",
            # in case of credentials it also contains "default" and "credentials


            base = "cloudmesh.entry" # get base from entry e.g. first two TODO

            access = base.split(".")[0:1]
            test = data[access[0]][access[1]]
            if Entry.verify(test, "credential"):
                config = Config() # todo: add the path
                config.update(_entry)
            else:
                Console.error("entry format is wrong")

        except yaml.YAMLError:
            Console.error("parsing YAML entry: {entry}")
            sys.exit()

    @staticmethod
    def verify(d, kind):
        valid = True
        if kind == "credential":
            for attribute in ["cm", "default", "credential"]:
                if  attribute not in d:
                    Console.error(f"{attribute} is not in the entry")
                    return False
        else:
            valid = False
        return valid



