from cloudmesh.common.parameter import Parameter
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate

#
# use CmDatabase for interacting with the db, you will find also a simple find
# function there.
#

class SecgroupDatabase():

    def __init__(self, type=None):
        self.type = type
        self.db = CmDatabase()
        self.cloud = "local"

    def clear(self):
        self.remove()

    def find(self, name=None):

        if name is None:
            query = {'cm.type': self.type}
        else:
            query = {'cm.type': self.type,
                     'cm.name': name}
        entries = self.db.find(collection=f"{self.cloud}-secgroup",
                               **query)
        return entries

    def remove(self, name=None):

        if name is None:
            query = {'cm.type': self.type}
        else:
            query = {'cm.type': self.type,
                     'cm.name': name}
        entries = self.db.delete(collection=f"{self.cloud}-secgroup",
                                 **query)
        return entries

    def list(self, name=None):
        found = []
        if name is None:
            # find all groups in the db
            found = self.find()
        else:
            # find only the grous specified in the db
            groups = Parameter.expand(name)
            for group in groups:
                try:
                    entry = self.find(name=name)[0]
                    found.append(entry)
                except:
                    pass

        return found

    def update_dict_list(self, entries):
        for entry in entries:
            entry['cm'] = {
                "kind": "secgroup",
                "name": entry['name'],
                "cloud": self.cloud,
                "type": self.type
            }
        return entries


class SecgroupRule(SecgroupDatabase):

    def __init__(self):
        super().__init__(type="rule")

    @DatabaseUpdate()
    def add(self, name=None, protocol=None, ports=None, ip_range=None):
        entry = {
            "name": name,
            "protocol": protocol,
            "ports": ports,
            "ip_range": ip_range,
        }
        return self.update_dict_list([entry])

    def delete(self, name=None):
        self.remove(name=name)


class Secgroup(SecgroupDatabase):

    def __init__(self):
        super().__init__(type="group")

    @DatabaseUpdate()
    def add(self,
            name=None,
            rules=None,
            description=None):
        """
        adds a rule to a given group. If the group does not exist, it will be created.

        :param group:
        :param rule:
        :return:
        """

        new_rules = rules
        if type(rules) == str:
            new_rules = Parameter.expand(rules)
        elif type(rules) == list:
            pass
        else:
            raise ValueError("rules have wrong type")

        try:
            entry = self.find(name=name)[0]
        except:
            entry = {
                'description': None,
                'rules': [],
                'name': name
            }

        if rules is not None:
            old = list(entry['rules'])
            entry['rules'] = list(set(new_rules + old))

        if description is not None:
            entry["description"] = description

        return self.update_dict_list([entry])

    @DatabaseUpdate()
    def delete(self, name=None, rules=None):
        """
        deletes the groups
        :param group:
        :return:
        """

        delete_rules = rules
        if type(rules) == str:
            delete_rules = Parameter.expand(rules)
        elif type(rules) == list:
            pass
        else:
            raise ValueError("rules have wrong type")
        delete_rules = set(delete_rules)

        entry = self.find(name=name)[0]

        if rules is not None:
            old = set(entry['rules'])
            old -= delete_rules
            entry['rules'] = list(old)

        return entry
