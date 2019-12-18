from cloudmesh.common.parameter import Parameter
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
from cloudmesh.common.Printer import Printer


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
    """
       "_id" : ObjectId("5dd766f3d860ed9e50f374c4"),
    "profile" : {
        "firstname" : "Nayeem",
        "lastname" : "Baig",
        "email" : "",
        "user" : "nayeemb",
        "github" : "nayeembaig",
        "publickey" : "~/.ssh/cloud.key.pub"
    },
    "path" : "/home/nayeem/.ssh/cloud.key.pub",
    "uri" : "file:///home/nayeem/.ssh/cloud.key.pub",
    "public_key" : "",
    "type" : "ssh-rsa",
    "key" : "",
    "comment" : "nayeem@DESKTOP-3SA2H9T",
    "fingerprint" : "",
    "name" : "nayeemb",
    "source" : "ssh",
    "location" : {
        "public" : "/home/nayeem/.ssh/cloud.key.pub",
        "private" : "/home/nayeem/.ssh/cloud.key"
    },
    "cm" : {
        "kind" : "key",
        "cloud" : "local",
        "name" : "nayeemb",
        "collection" : "local-key",
        "created" : "2019-11-22 04:41:23.181287",
        "modified" : "2019-11-29 15:39:47.850334"
    }

    """
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
    def add(self, name=None):
        """
        adds a key to a given group. If the group does not exist, it will be
        created.

        :param name:
        :param keys:
        :return:
        """

        new_key = name
        if type(name) == str:
            new_key = Parameter.expand(name)
        elif type(name) == list:
            pass
        else:
            raise ValueError("key have wrong type")

        # noinspection PyUnusedLocal
        try:
            entry = self.find(name=name)[0]
        except Exception as e:
            entry = {
                'name': name
            }

        if name is not None:
            old = list(entry['name'])
            entry['name'] = list(set(new_key + old))

        return self.update_dict_list([entry])

    @DatabaseUpdate()
    def delete(self, name=None):
        """
        deletes the groups
        :param name:
        :param rules:
        :return:
        """

        delete_key = name
        if type(name) == str:
            delete_key = Parameter.expand(name)
        elif type(name) == list:
            pass
        else:
            raise ValueError("key have wrong type")
        delete_key = set(delete_key)

        entry = self.find(name=name)[0]

        if name is not None:
            old = set(entry['key'])
            old -= delete_key
            entry['key'] = list(old)

        return entry
