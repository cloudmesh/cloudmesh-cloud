from cloudmesh.common.DictList import DictList
from cloudmesh.common.parameter import Parameter
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate


class Group(object):
    """
    Groups are used to store the names of services that are part of the
    group. Members are identified by their name and the kind (such as vm).

    The data of a group is managed via a dict. Here is a simple example

    cm:
      name: test
      cloud: local
      kind: group
    members:
    - name: vm-1
      kind: vm
    - name: vm-2
      kind: vm
    - name: vm-3
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

    def delete_group(self, name=None):
        raise NotImplementedError

    def delete_member(self, name=None, member=None):
        """
        delete the member from the group

        :param name: name of the group
        :param member: name of the member
        :return:
        """
        raise NotImplementedError

    def copy_group(self, source, destination):
        """
        copies the group source to destination

        :param source: name of the source
        :param destination: name of the destination
        :return:
        """
        raise NotImplementedError

    def merge(self, destination, *groups):
        """
        merge the members of the groups into the destination group

        :param destination:
        :param groups:
        :return:
        """
        raise NotImplementedError

    def members(self, name=None):
        r = self.list(name=name)
        members = r[0]['members']
        return members

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

        for entry in entries:
            result.append(entry)
        return result

    #
    # not tested when data is already in db
    #
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

        entries = [{'name': service, 'kind': category} for
                   service in services]

        for entry in old:
            if entry not in entries:
                entries.append(old[entry])

        entry['members'] = entries

        return [entry]
