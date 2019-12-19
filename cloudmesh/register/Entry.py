from cloudmesh.configuration.Config import Config
from textwrap import dedent
import oyaml as yaml
from cloudmesh.common.console import Console
import sys
from pprint import pprint
from copy import deepcopy

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
    def extract(data, base):
        location = base.split(".")
        _data = deepcopy(data)
        for i in location:
            _data = _data[i]
        name = list(_data.keys())[0]
        _data = _data[name]
        return name, _data

    @staticmethod
    def add(entry=None,
            base = "cloudmesh.compute",
            path="~/.cloudmesh/cloudmesh.yaml"):

        try:
            _entry = dedent(entry)
            print (_entry)
            data = yaml.safe_load(_entry)

            pprint (data)
            # verify format
            # cloudmesh.entry contains "cm",
            # in case of credentials it also contains "default" and "credentials



            if Entry.verify(data, "credential", base=base):
                Console.ok("Verification passed")

                name, entry = Entry.extract(data, base)

                pprint (entry)


                print ("NAME", name)



                config = Config() # todo: add the path
                config[base][name] = data

                #config.save()

            else:
                Console.error("entry format is wrong")

        except yaml.YAMLError:
            Console.error(f"parsing YAML entry: {entry}")
            sys.exit()

    @staticmethod
    def verify(data, kind, base):


        _data = Entry.extract(data, base)
        pprint (_data)
        valid = True
        for attribute in ["cm", "default", "credentials"]:
            if attribute not in _data:
                Console.error(f"{attribute} is not in the entry")
                return False
            else:
                Console.ok(f"{attribute} is in the entry")
        return valid



