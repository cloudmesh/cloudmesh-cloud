from cloudmesh.common.parameter import Parameter

#
# use CmDatabase for interacting with the db, you will find also a simple find
# function there.
#

class SecgroupRule(object):

    def __init__(self):
        pass

    def add(self, rule, fromport, toport, protocol, cidr):
        raise NotImplementedError

    def delete(self, rule=None):
        rules = Parameter.expand(rule)
        # delete the rules
        for rule in rules:
            # delete the rule in the db
            raise NotImplementedError

        raise NotImplementedError

    def list(self, rule=None):
        found = []
        if rule is None:
            # find all rules in the db
            found = []
            raise NotImplementedError
        else:
            rules = Parameter.expand(rule)
            # find only the rules specified in the db
            find = []
            raise NotImplementedError
        found = self.update_dict_list(entries)
        return found

    def update_dict_list(self, entries, name):
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
        pass

    def add(self, group, rule):
        """
        adds a rule to a given group. If the group does not exist, it will be created.

        :param group:
        :param rule:
        :return:
        """
        entry = None # find the entry in the db
        found = self.update_dict_list(entry)
        raise NotImplementedError

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

    def update_dict_list(self, entries, name):
        for entry in entries:
            entry['cm'] = {
                "kind": "secgroup",
                "name": entry['name'],
                "cloud": "local",
                "type": "group"
            }
        return entries
