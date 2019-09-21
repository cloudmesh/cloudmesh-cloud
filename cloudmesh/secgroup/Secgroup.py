from cloudmesh.common.parameter import Parameter
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate


#
# use CmDatabase for interacting with the db, you will find also a simple find
# function there.
#

class SecgroupExamples:

    def __init__(self):

        self.secgroups = {

            "default": {
                "description": "Default security group",
                "rules": [
                    "ssh", "icmp", "http", "https"
                ]
            },
            "flask": {
                "description": "Flask security group",
                "rules": [
                    "ssh", "icmp", "http", "https", "flask"
                ]
            }
        }

        self.secrules = {
            "ssh": {
                "protocol": "tcp",
                "ip_range": "0.0.0.0/0",
                "ports": "22:22",
            },
            "icmp": {
                "protocol": "icmp",
                "ip_range": "0.0.0.0/0",
                "ports": "",
            },
            "flask": {
                "protocol": "tcp",
                "ip_range": "0.0.0.0/0",
                "ports": "8000:8000",
            },
            "http": {
                "protocol": "tcp",
                "ip_range": "0.0.0.0/0",
                "ports": "80:80",
            },
            "https": {
                "protocol": "tcp",
                "ip_range": "0.0.0.0/0",
                "ports": "443:443",
            },
        }

    def rule(self, name, cm=False):
        data = dict(self.secrules[name])
        data['name'] = name
        if cm:
            data['cm'] = {
                "kind": "secrule",
                "name": str(name),
                "cloud": "local",
            }
        return data

    def group(self, name, cm=False):
        data = dict(self.secgroups[name])
        data['name'] = name
        if cm:
            data['cm'] = {
                "kind": "secgroup",
                "name": str(name),
                "cloud": "local",
            }
        return data

    @DatabaseUpdate()
    def load(self, cm=False):
        groups = Secgroup()
        rules = SecgroupRule()

        data = []

        print()
        for name in self.secgroups:
            entry = self.group(name, cm=cm)
            data.append(groups.update_dict_list([entry])[0])

        for name in self.secrules:
            entry = self.rule(name, cm=cm)
            data.append(rules.update_dict_list([entry])[0])

        return data


class SecgroupDatabase:

    # noinspection PyShadowingBuiltins
    def __init__(self, kind=None):
        self.kind = kind
        self.cm = CmDatabase()
        self.cloud = "local"
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
        entries = self.cm.delete(collection=self.collection,
                                 **query)
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


class SecgroupRule(SecgroupDatabase):

    def __init__(self):
        super().__init__(kind="secrule")

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
    output = {
        "all": {
            "sort_keys": ["group", "rule"],
            "order": ["group",
                      "rule",
                      "protocol",
                      "ports",
                      "ip_range"],
            "header": ["Group",
                       "Rule",
                       "Protocol",
                       "Ports",
                       "IP Range"]
        },
        "secrule": {
            "sort_keys": ["name"],
            "order": ["name",
                      "protocol",
                      "ports",
                      "ip_range"],
            "header": ["Name",
                       "Protocol",
                       "Ports",
                       "IP Range"]
        },
        "secgroup": {
            "sort_keys": ["name"],
            "order": ["name",
                      "rules",
                      "description"],
            "header": ["Name",
                       "Rules",
                       "Description"]
        }

    }

    def __init__(self):
        super().__init__(kind="secgroup")

    # noinspection PyBroadException
    @DatabaseUpdate()
    def add(self,
            name=None,
            rules=None,
            description=None):
        """
        adds a rule to a given group. If the group does not exist, it will be
        created.

        :param name:
        :param rules:
        :param description:
        :return:
        """

        new_rules = rules
        if type(rules) == str:
            new_rules = Parameter.expand(rules)
        elif type(rules) == list:
            pass
        else:
            raise ValueError("rules have wrong type")

        # noinspection PyUnusedLocal
        try:
            entry = self.find(name=name)[0]
        except Exception as e:
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
        :param name:
        :param rules:
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
