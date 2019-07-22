import oyaml as yaml
from cloudmesh.common.parameter import Parameter
from cloudmesh.common3.DictList import DictList
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate


class Group(object):
    """
    group elements are dicts that point to information in the cloudmesh database.
    group membership is identified by an element being registered into a group.
    An element can be part of multiple groups.

    An group entry must uniquely be able to identify the object that is part of
    the group.

    Here is a simple example

    cm:
      name: group
      cloud: local
      kind: group
    members:
    - vm-1:
        name: vm-1
        kind: vm
    - vm-2:
        name: vm-2
        kind: vm
    - vm-3:
        name: vm-3
        kind: vm


    """

    def __init__(self):
        self.kind = "group"
        self.cloud = "local"
        self.name = 'group'

    def update_list(self, d):
        cm = {
            "name": self.name,
            "cloud": self.cloud,
            "kind": self.kind
        }
        for entry in d:
            entry['cm'].update(cm)
        return d

    def list(self, name=None):
        cm = CmDatabase()
        result = []

        if name:
            col = cm.collection(name=f"{self.cloud}-{self.name}")
            entries = col.find_one({"cm.kind": 'group',
                                    "cm.cloud": 'local',
                                    "cm.name": name
                                    }, {"_id": 0})
            return [entries]
        else:
            entries = cm.find(collection=f"{self.cloud}-{self.name}")

            print("PPPP", entries)

        for entry in entries:
            result.append(entry)
        return result

    @DatabaseUpdate()
    def add(self,
            name=None,
            services=None,
            category=None):
        # check if non and raise error

        if type(services) == str:
            services = Parameter.expand(services)

        # cm = CmDatabase()

        entry = {
            'cm': {
                "name": name,
                "cloud": self.cloud,
                "kind": self.kind
            }
        }

        entry['members'] = []  # find in db

        old = DictList(entry['members'])

        entries = [{service: {'name': service, 'kind': category}} for
                   service in services]

        for entry in old:
            if entry not in entries:
                entries.append(old[entry])

        entry['members'] = entries

        print(yaml.dump(entry))

        return [entry]

    def delete(self, elements):
        raise NotImplementedError

    def merge(self, group_a, group_b, group_c):
        raise NotImplementedError

    def remove(self, group, elements):
        raise NotImplementedError

    def terminate(self, group, filter):
        raise NotImplementedError

    def status(self, group, filter):
        raise NotImplementedError
