from cloudmesh.common.parameter import Parameter
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
from cloudmesh.common.debug import VERBOSE
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.common.variables import Variables
#
# use CmDatabase for interacting with the db, you will find also a simple find
# function there.
#

class SecgroupRule(object):

    def __init__(self):
        self.db = CmDatabase()

    @DatabaseUpdate()
    def add(self, name=None, protocol=None, ports=None, ip_range=None):
        entry = {
            "name": name,
            "protocol": protocol,
            "ports": ports,
            "ip_range": ip_range,
        }
        VERBOSE(entry)
        return self.update_dict_list([entry])

    def delete(self, name=None):
        rules = Parameter.expand(name)
        # delete the rules
        for rule in rules:
            # delete the rule in the db
            raise NotImplementedError

        raise NotImplementedError

    def list(self, name=None):
        found = []
        if name is None:
            # find all rules in the db
            found = []
            raise NotImplementedError
        else:
            rules = Parameter.expand(name)
            # find only the rules specified in the db
            find = []
            raise NotImplementedError
        found = self.update_dict_list(entries)
        return found

    def update_dict_list(self, entries):
        for entry in entries:
            entry['cm'] = {
                "kind": "secgroup",
                "name": entry['name'],
                "cloud": "local",
                "type": "rule"
            }
        return entries

class Secgroup(object):

    def __init__(self):
        self.db = CmDatabase()


    def find(self, name=None):

        cloud = "local"
        db = CmDatabase()
        if name is None:
            query = {'cm.type': "group"}
        else:
            query = {'cm.type':"group",
                     'cm.name': name}
        entries = db.find(collection=f"{cloud}-secgroup",
                          **query)
        return entries


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

        entry = self.find(name=name)[0]

        if rules is not None:

            old = list(entry['rules'])
            entry['rules'] = list(set( new_rules + old ) )

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



    def list(self, name=None):
        found = []
        if name is None:
            # find all groups in the db
            found =  self.find()[0]
        else:
            # find only the grous specified in the db
            groups = Parameter.expand(name)
            find = []
            for group in groups:
                entry = self.find(name=name)[0]
                found.append(entry)
        return found

    def update_dict_list(self, entries):
        for entry in entries:
            entry['cm'] = {
                "kind": "secgroup",
                "name": entry['name'],
                "cloud": "local",
                "type": "group"
            }
        return entries
