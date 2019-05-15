from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate


class Group(object):
    """
    group elements are dicts that point to information in the cloudmesh database.
    group membership is identified by an element being registered into a group.
    An element can be part of multiple groups.

    An group entry must uniquely be able to identify the object that is part of
    the group.

    Here a simple example

    group:
      cm:
        kind: group
        name: name of group
        cloud: grou        # will be renamed in future to service
      members:
        name01:
          cm:
            kind: vm
            name: node01
            cloud: aws
        name02:
          cm:
            kind: vm
            name: node02
            cloud: aws
        storage:
          cm:
            kind: vm
            name: data
            cloud: box

    elements to be added to the group are simple dicts of the form

    cm:
        kind:
        name:
        cloud:

    these can be used to identify the collection of the group member to retrive
    mor detailed information as part of the list function.

    A filter can be specified to reduce the results.

    """

    def list(self, group=None):
        cm = CmDatabase()
        entries = []
        try:
            cursor = cm.find_group(group)
            for entry in cursor:
                entries.append(entry)
        except Exception as e:
            pass
        return entries

    @DatabaseUpdate()
    def add(self, services=None, group=None):
        # check if non and raise error

        cm = CmDatabase()
        entries = []
        for service in services:
            try:
                entry = dict(cm.find_name(service)[0])
                del entry["_id"]
                entry["cm"]["group"] = group
                entries.append(entry)
            except Exception as e:
                break
        return entries

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
