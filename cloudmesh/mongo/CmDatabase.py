import urllib.parse
from datetime import datetime

from pymongo import MongoClient

from cloudmesh.management.configuration.config import Config
from cloudmesh.common.console import Console

from pprint import pprint


#
# cm:
#   id:
#   user:
#   experiment:
#   kind:
#   group:

class CmDatabase(object):
    __shared_state = {}

    def __init__(self, host=None, username=None, password=None, port=None):

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

    def connect(self):
        """
        connect to the database
        """
        self.client = MongoClient(
            f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}")
        self.db = self.client[self.database]

    def collection(self, name):
        return self.db[name]

    def close_client(self):
        """
        close the connection to the database
        """
        self.client.close()

    def find(self, collection="cloudmesh", **kwrags,):
        col = self.db[collection]

        entries = col.find(kwrags, {"_id": 0})

        records = []
        for entry in entries:
            records.append(entry)
        return records

    def find_by_id(self, cmid, collection="cloudmesh"):

        entry = self.find(collection=collection, cmid=cmid)

        return entry

    def find_by_counter(self, cmcounter, collection="cloudmesh"):

        entry = self.find(collection=collection, cmcounter=cmcounter)

        return entry

    def update(self, entries):

        print("YYYY", type(entries))
        for entry in entries:
            entry['collection'] = "{cloud}-{kind}".format(**entry)

            # entry["collection"] = collection
            try:
                self.col = self.db[entry['collection']]

                data = self.col.find_one({"kind": entry["kind"],
                                          "cloud": entry["cloud"],
                                          "name": entry["name"]
                                          })
                if data is not None:
                    entry['created'] = data['created']
                    entry['modified'] = str(datetime.utcnow())
                    self.col.update({
                        "kind": entry["kind"],
                        "cloud": entry["cloud"],
                        "name": entry["name"]
                    },
                        entry,
                        upsert=True)
                else:
                    entry['created'] = entry['modified'] = str(
                        datetime.utcnow())
                    self.col.insert(entry)
            except Exception as e:
                Console.error("uploading document {entry}".format(
                    entry=str(entry)))
                pass

        result = entry
        return result

    def insert(self, d, collection="cloudmesh"):
        col = self.db[collection]
        col.insert_one(d)

    def update_old(self,
                   entries,
                   collection="cloudmesh",
                   replace=False,
                   **kwargs):
        """

        :param entries: an arrey of dicts where one entry is called cmid.
                        One must be carefulas it does not erase previous attributes.
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

            pprint(entry)
            name = entry['name']

            if kwargs is not None:
                for arg in kwargs:
                    entry[arg] = kwargs[arg]
            entry["updated"] = str(datetime.utcnow())
            if replace:
                col.replace_one({'name': entry[name]}, entry, upsert=True)
            else:
                col.update_one({'name': entry[name]}, {"$set": entry},
                               upsert=True)

    def delete(self, collection="cloudmesh", **kwargs):
        col = self.db[collection]
        col.delete_one(**kwargs)

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

    def status(self):
        """
        test mongodb correspondent db connection
        :return:
        """
        return self.command("serverStatus")

    def clear(self, collection="cloudmesh"):
        """
        remove all entries from mongo
        :return:
        """

        col = self.db[collection]
        col.drop()



