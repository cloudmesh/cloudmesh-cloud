from cloudmesh.common.parameter import Parameter
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
from cloudmesh.common.Printer import Printer
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.key.Key import Key

class KeyGroupDatabase:

    # noinspection PyShadowingBuiltins
    def __init__(self, cloud="local", kind="keygroup"):
        self.kind = kind
        self.cloud = cloud
        self.cm = CmDatabase()
        self.collection = f"{self.cloud}-{kind}"

    def clear(self):
        self.cm.collection(self.collection).delete_many({})

    def find(self, name=None):

        if name is None:
            query = {}
        else:
            query = {'cm.name': name}
        entries = self.cm.find(collection=self.collection, query=query)
        return entries

    def remove(self, name=None):

        if name is None:
            query = {}
        else:
            query = {'cm.name': name}
        entries = self.cm.delete(collection=self.collection, **query)
        return entries

    # noinspection PyBroadException
    def list(self, name=None):
        found = []
        if name is None:
            # find all groups in the db
            found = self.find()
        else:
            # find only the groups specified in the db
            groups = Parameter.expand(name)
            # noinspection PyUnusedLocal
            for group in groups:
                # noinspection PyUnusedLocal
                try:
                    entry = self.find(name=name)[0]
                    found.append(entry)
                except Exception as e:
                    pass

        return found

    def update_dict_list(self, entries):
        for entry in entries:
            entry['cm'] = {
                "kind": self.kind,
                "name": entry['name'],
                "cloud": self.cloud
            }
        return entries

class KeyGroup(KeyGroupDatabase):
    output = {
        "key": {
            "sort_keys": ["name"],
            "order": ["name",
                      "comment",
                      "fingerprint",
                      "profile.publickey"
                      ],
            "header": ["Name",
                       "Comment",
                       "Fingerprint",
                       "Publickey"
                       ]
        },
        "keygroup": {
            "sort_keys": ["name"],
            "order": ["name",
                      "keys"],
            "header": ["Name",
                       "Keys"]
        }

    }

    # noinspection PyPep8Naming
    def Print(self, data, output=None, kind=None):

        if output == "table":
            if kind == "key" or kind == 'keygroup':
                result = []
                for group in data:
                    result.append(group)
                data = result

            order = self.output[kind]['order']  # not pretty
            header = self.output[kind]['header']  # not pretty

            print(Printer.flatwrite(data,
                                    sort_keys=["name"],
                                    order=order,
                                    header=header,
                                    output=output,
                                    # humanize=humanize
                                    )
                  )
        else:
            print(Printer.write(data, output=output))

    def __init__(self, cloud="local"):
        super().__init__(cloud, kind="keygroup")

    # noinspection PyBroadException
    @DatabaseUpdate()
    def add(self, groupname=None, keyname=None):
        """
        adds a key to a given group. If the group does not exist, it will be
        created.

        :param groupname:
        :param keyname:
        :return:
        """
        # print('In KeyGroup')
        # print('name: ' , keyname)
        new_key = keyname
        if type(keyname) == str:
            new_key = Parameter.expand(keyname)
        elif type(keyname) == list:
            pass
        else:
            raise ValueError("key have wrong type")

        # noinspection PyUnusedLocal
        try:
            entry = self.find(name=groupname)[0]
        except Exception as e:
            entry = {
                'name': groupname,
                'keys': [keyname]
            }

        if groupname is not None:
            entry['keys'] += list(set(new_key))
            entry['keys'] = list(set(entry['keys']))
        else:
            entry['keys'] = list(set(new_key))

        return self.update_dict_list([entry])

    @DatabaseUpdate()
    def delete(self, groupname=None, keyname=None):
        """
        deletes the key from group
        :param groupname:
        :param keyname:
        :return:
        """
        delete_key = keyname
        if type(keyname) == str:
            delete_key = Parameter.expand(keyname)
        elif type(keyname) == list:
            pass
        else:
            raise ValueError("key have wrong type")
        delete_key = set(delete_key)

        entry = self.find(name=groupname)[0]

        if groupname is not None:
            old = set(entry['keys'])
            old -= delete_key
            entry['keys'] = list(old)

        return entry

    #
    # BUG: passing cloud is not needed
    # CHECK: does the command work with >>
    #
    def upload(self, group=None, cloud=None, vm=None):

        # key group upload [--group=GROUPNAMES] [--cloud=CLOUDS] [ip/vm]

        groupkeys = group

        db_keys = self.cm.find(collection=f"{self.cloud}-key")
        db_keygroups = self.cm.find(collection=f"{self.cloud}-keygroup")

        keygroups = []
        for groups in db_keygroups:
            if groups["name"] == groupkeys:
                for x in groups["keys"]:
                    keygroups.append(x)

        provider = Provider(name=cloud)
        keys = ""
        for key in db_keys:
            if key["name"] in keygroups:
                keys += key["public_key"]
                keys += "\n"
                command = "echo " + keys + " >> " + "$HOME/.ssh/authorized_keys"
                # print(command, "\n")
                provider.ssh(vm, command)

    #
    # BUG: this seems to just list the collection names?
    # BUG: print keys and keygroups missing
    #
    def list_groups_broken(self, group=None):

        key = KeyGroup()

        groups = Parameter.expand(group)

        db_keys = self.cm.find(collection=f"{self.cloud}-key")
        db_keygroups = self.cm.find(collection=f"{self.cloud}-keygroup")

        return db_keys, db_keygroups

    def add_broken(self, groups=None, names=None, name=None, filename=None, cloud=None):

         #key group add --group=abc [NAMES]

        names = Parameter.expand(names)

        if filename is not None:
            key = Key()
            key.add(name, filename)

        db_keys = self.cm.find(collection=f"{cloud}-key")
        keys = self.get_key_list(db_keys, names)

        for i in keys:
            key.add(groups, i)

        #if list(set(names) - set(keys)) is not None:
        #    print('Keys dont exist, please add them', list(set(names) - set(keys)))

    def export_broken(self, group=None, filename=None):
        # key group export --group=GROUPNAMES --file=FILENAME

        groupkeys = group

        db_keys = self.cm.find(collection=f"{self.cloud}-key")
        db_keygroups = self.cm.find(collection=f"{self.cloud}-keygroup")

        keygroups = []
        for groups in db_keygroups:
            if groups["name"] == groupkeys:
                for x in groups["keys"]:
                    keygroups.append(x)

        keys = ""
        for key in db_keys:
            if key["name"] in keygroups:
                keys += key["public_key"]
                keys += "\n"

        sample = open(filename, 'a+')
        sample.close()

    def get_key_list(self, db_keys, names):
        keys = []
        for key in db_keys:
            for i in names:
                if key["name"].strip() == i.strip():
                    keys.append(key["name"])

        return keys

