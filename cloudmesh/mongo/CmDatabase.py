import urllib.parse
from datetime import datetime

from cloudmesh.common.console import Console
from cloudmesh.common.parameter import Parameter
from cloudmesh.management.configuration.config import Config
from pymongo import MongoClient


#
# cm:
#   id:
#   user:
#   experiment:
#   kind:
#   group:

class CmDatabase(object):
    __shared_state = {}

    # ok
    def __init__(self, host=None, username=None, password=None, port=None):
        """
        create a cloudmesh database in the specified mongodb

        :param host: the host
        :param username: the username
        :param password: the password
        :param port: the port
        """

        self.__dict__ = self.__shared_state
        if "cnfig" not in self.__dict__:

            self.config = Config().data["cloudmesh"]
            self.mongo = self.config["data"]["mongo"]
            self.mongo["MONGO_PASSWORD"] = str(self.mongo["MONGO_PASSWORD"])

            self.database = self.mongo["MONGO_DBNAME"]
            self.host = host or self.mongo["MONGO_HOST"]
            self.password = urllib.parse.quote_plus(
                str(password or self.mongo["MONGO_PASSWORD"]))
            self.username = urllib.parse.quote_plus(
                str(username or self.mongo["MONGO_USERNAME"]))
            if port is None:
                self.port = int(self.mongo["MONGO_PORT"])
            else:
                self.port = int(port)

            self.client = None
            self.db = None

            self.connect()

    # ok
    def connect(self):
        """
        connect to the database
        """
        self.client = MongoClient(
            f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}")
        self.db = self.client[self.database]

    # ok
    def collection(self, name):
        """
        returns the named collection
        :param name: the collection name
        :return: teh collection
        """
        return self.db[name]

    # ok
    def close_client(self):
        """
        close the connection to the database
        """
        self.client.close()

    # ok
    def collections(self):
        """
        the names of all collections
        :return: list of names of all collections
        """
        return self.db.collection_names()

    # ok
    def name_count(self, name):
        """
        counts the occurence of the name used in the collections

        :param name: the name
        :return:
        """
        count = 0
        collections = self.collections()
        for collection in collections:
            entry = self.find({"collection": collection, "cm.name": entry})
            count = count + len(entry)
        return count

    # ok
    def find_name(self, name):
        """
        This function returns the entry with the given name from all collections
        in mongodb. The name must be unique accross all collections

        :param name: the unique name of the entry
        :return:
        """
        entry = []
        collections = self.collections()
        for collection in collections:
            entry = self.find({"collection": collection, "cm.name": entry})
            if len(entry) > 0:
                return entry
        return entry

    # ok
    def find_names(self, names):
        """
        Assuming names specified as parameters, it returns the entries with
        these anmes from all collections in mongodb. The names must be unique
        across all collections.

        :param names: the unique names in parameter format
        :return:
        """
        result = []
        entries = Parameter.expand(names)
        if len(entries) > 0:
            for entry in entries:
                r = self.find_name({"cm.name": entry})
                if r is not None:
                    result.append(r[0])
        return result

    """
    # check
    def find(self, query):
        col = self.db[query["collection"]]

        entries = col.find(query, {"_id": 0})

        records = []
        for entry in entries:
            records.append(entry)
        return records
    """

    # check TODO BUG see previous
    def find(self, collection="cloudmesh", **kwargs):
        col = self.db[collection]

        entries = col.find(kwargs, {"_id": 0})

        records = []
        for entry in entries:
            records.append(entry)
        return records

    # check
    def find_by_id(self, cmid, collection="cloudmesh"):

        entry = self.find(collection=collection, cmid=cmid)

        return entry

    # check
    def find_by_counter(self, cmcounter, collection="cloudmesh"):

        entry = self.find(collection=collection, cmcounter=cmcounter)

        return entry

    # check
    def update(self, entries):

        result = []
        for entry in entries:

            if 'cm' not in entry:
                raise ValueError("The cm attribute is not in the entry")
            entry['cm']['collection'] = "{cloud}-{kind}".format(**entry["cm"])

            # noinspection PyUnusedLocal
            try:
                self.col = self.db[entry['cm']['collection']]

                data = self.col.find_one({"cm.kind": entry["cm"]["kind"],
                                          "cm.cloud": entry["cm"]["cloud"],
                                          "cm.name": entry["cm"]["name"]
                                          })

                if data is not None:
                    entry['cm']['created'] = data["cm"]['created']
                    entry['cm']['modified'] = str(datetime.utcnow())
                    self.col.update(
                        {
                            "cm.kind": entry['cm']["kind"],
                            "cm.cloud": entry['cm']["cloud"],
                            "cm.name": entry['cm']["name"]
                        },
                        entry,
                        upsert=True)
                else:
                    entry['cm']['created'] = entry['cm']['modified'] = str(
                        datetime.utcnow())
                    self.col.insert(entry)
            except Exception as e:
                Console.error("uploading document {entry}".format(
                    entry=str(entry)))
                pass
            result.append(entry)

        return result

    def alter(self, entries):
        # for entry in entries:
        for entry in entries:
            try:
                # self.db["{cloud}-{kind}".format(**entry)].update(uniqueKeyVal,{'$set': keyvalToUpdate})
                entry['modified'] = str(datetime.utcnow())
                self.db["{cloud}-{kind}".format(**entry)].update({'cm': entry['cm']}, {'$set': entry})
            except Exception as e:
                Console.error("modifying document {entry}".format(
                    entry=str(entry)))
                pass
        return entries

    def exists(self, entries):
        '''
        Check if entry exists in the database
        :param entries:
        :return:
        '''
        exist_status = []
        if type(entries) is dict:
            entries = [entries]
        for entry in entries:
            collection = self.db["{cloud}-{kind}".format(**entry)]
            status = collection.find({'cm': {'$exists': entry['cm']}}).count() > 0
            exist_status.append(status)
        return exist_status

    # check
    def insert(self, d, collection="cloudmesh"):
        col = self.db[collection]
        col.insert_one(d)

    # remove
    def update_old(self,
                   entries,
                   collection="cloudmesh",
                   replace=False,
                   **kwargs):
        """

        :param entries: an array of dicts where one entry is called cmid.
                        One must be careful as it does not erase previous attributes.
        :param collection:
        :param replace:
        :return:
        """
        if type(entries) == dict:
            _entries = [entries]
        else:
            _entries = entries

        col = self.db[collection]

        for entry in _entries:

            # pprint(entry)
            name = entry['name']

            if kwargs is not None:
                for arg in kwargs:
                    entry[arg] = kwargs[arg]
            entry["updated"] = str(datetime.utcnow())
            if replace:
                col.update({'name': entry[name]}, entry, upsert=True)
            else:
                col.update_one({'name': entry[name]}, {"$set": entry},
                               upsert=True)

    # check
    def delete(self, collection="cloudmesh", **kwargs, ):
        col = self.db[collection]
        col.delete_one(**kwargs)

    # check
    def command(self, command):
        """
        issue command string via the mongoDB console
        :param command: interaction command string you want to send to mongodb console
        :return: command return
        """
        # noinspection PyUnusedLocal
        try:
            res = self.db.command(command)
        except Exception as e:
            # print(e)
            raise ValueError("Not a valid command")

        return res

    # ok
    def status(self):
        """
        test mongodb correspondent db connection
        :return:
        """
        return self.command("serverStatus")

    # ok
    def clear(self, collection="cloudmesh"):
        """
        drops the collection
        :return:
        """

        col = self.db[collection]
        col.drop()
