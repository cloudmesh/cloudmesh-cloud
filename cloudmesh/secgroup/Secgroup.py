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


    def find(self, **kwargs):
        cloud = "local"
        entries = self.db.find(collection=f"{cloud}-image", **kwargs)
        return entries

    @DatabaseUpdate()
    def add(self, group=None, rule=None):
        """
        adds a rule to a given group. If the group does not exist, it will be created.

        :param group:
        :param rule:
        :return:
        """
        # not sure how to do the query yet
        entry = self.find({"cm.type":"group"}) # find the entry in the db

        # update it
        return self.update_dict_list(entry)

    def delete(self, group=None):
        """
        deletes the groups
        :param group:
        :return:
        """
        groups = Parameter.expand(group)
        for group in groups:
            # delete the group in the db
            raise NotImplementedError

    def list(self, group=None):
        found = []
        if group is None:
            # find all groups in the db
            found = []
            raise NotImplementedError
        else:
            groups = Parameter.expand(group)
            # find only the grous specified in the db
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
                "type": "group"
            }
        return entries
