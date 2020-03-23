import re
import urllib.parse
from datetime import datetime

from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.parameter import Parameter
from cloudmesh.configuration.Config import Config
from cloudmesh.mongo.MongoDBController import MongoDBController
from progress.bar import Bar
from pymongo import MongoClient
import json
import os
from sys import platform
import subprocess
import ctypes
import shutil
import re


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
        if "config" not in self.__dict__:

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
        MongoDBController().start_if_not_running()
        return self.db[name]

    # ok
    def close_client(self):
        """
        close the connection to the database
        """
        self.client.close()

    # ok
    def collections(self, name=None, regex=None):
        """
        the names of all collections

        :param name: if set, only look at these collections instead of all
                     collections
        :param regex: a regular expression on the names of the collections
        :return: list of names of all collections

        Example:
            collections = cm.collections(regex=".*-vm")
        """
        MongoDBController().start_if_not_running()
        names = None
        if name:
            if type(name) == list:
                names = name
            else:
                names = Parameter.expand(name)
        else:
            names = self.db.collection_names()
        if regex:
            r = re.compile(regex)
            _names = list(filter(r.match, names))
            names = _names
        return names

    # ok
    # noinspection PyPep8
    def name_count(self, name):
        """
        counts the occurrence of the name used in the collections

        :param name: the name
        :return:
        """
        MongoDBController().start_if_not_running()
        count = 0
        collections = self.collections()
        for collection in collections:
            try:
                entry = self.find({"cm.name": name})
                count = count + len(entry)
            except:
                pass
        return count

    # ok
    def find_group(self, name):
        """
        This function returns the entry with the given name from all collections
        in mongodb. The name must be unique across all collections

        :param name: the unique name of the entry
        :return:
        """
        MongoDBController().start_if_not_running()
        entries = []
        collections = self.collections()
        for collection in collections:
            try:
                col = self.db[collection]
                cursor = col.find({"cm.group": name})
                for entry in cursor:
                    entries.append(entry)
            except Exception as e:
                print(e)
                pass
        return entries

    # ok
    # noinspection PyPep8
    def find_name(self, name, kind=None):
        """
        This function returns the entry with the given name from all collections
        in mongodb. The name must be unique across all collections

        :param name: the unique name of the entry
        :return:
        """
        MongoDBController().start_if_not_running()
        entries = []
        if kind is None:
            collections = self.collections()
        else:
            collections = self.collections(regex=f".*-{kind}")

        for collection in collections:
            try:
                col = self.db[collection]
                if kind is None:
                    cursor = col.find({"cm.name": name})
                else:
                    cursor = col.find({"cm.name": name, "cm.kind": kind})
                for entry in cursor:
                    entries.append(entry)
            except:
                pass
            if cursor.count() > 0:
                return entries
        return entries

    def find_all_by_name(self, name, kind=None):
        """
        This function returns the entry with the given name from all collections
        in mongodb. The name must be unique across all collections

        :param name: the unique name of the entry
        :return:
        """
        MongoDBController().start_if_not_running()
        entries = []
        if kind is None:
            collections = self.collections()
        else:
            collections = self.collections(regex=f".*-{kind}")

        for collection in collections:
            try:
                col = self.db[collection]
                if kind is None:
                    cursor = col.find({"cm.name": name})
                else:
                    cursor = col.find({"cm.name": name, "cm.kind": kind})
                for entry in cursor:
                    entries.append(entry)
            except:
                pass
        return entries

    # ok
    def find_names(self, names):
        """
        Assuming names specified as parameters, it returns the entries with
        these names from all collections in mongodb. The names must be unique
        across all collections.

        :param names: the unique names in parameter format
        :return:
        """
        MongoDBController().start_if_not_running()
        result = []
        entries = Parameter.expand(names)
        if len(entries) > 0:
            for entry in entries:
                r = self.find_name(entry)
                if r is not None:
                    result.append(r[0])
        return result

    # ok
    def names(self, collection=None, cloud=None, kind=None, regex=None):
        """
        finds all names in the specified collections. The parameters,
        collection, cloud, and kind can all be Parameters that get expanded
        to lists. All names from all collections are merged into the result.

        With kwargs a search query on the names could be added.

        Example:
            cm = CmDatabase()
            for kind in ['vm', "image", "flavor"]:
                names = cm.names(cloud="chameleon", kind=kind)
            print (names)

            names = cm.names(cloud="chameleon,azure", kind="vm")
            names = cm.names(collection="chameleon-image", regex="^CC-")
            names = cm.names(collection="chameleon-image", regex=".*Ubuntu.*")

        :param collection: The collections
        :param cloud: The clouds
        :param kind: The kinds
        :param regex: A query applied to name
        :return:
        """
        MongoDBController().start_if_not_running()
        collections = Parameter.expand(collection)
        clouds = Parameter.expand(cloud)
        kinds = Parameter.expand(kind)
        result = []

        def add(collection):
            col = self.db[collection]
            if not regex:
                entries = col.find({}, {"name": 1, "_id": 0})
            else:
                entries = col.find(
                    {"name": {'$regex': regex}},
                    {"name": 1, "_id": 0})
            for entry in entries:
                result.append(entry['name'])

        #
        # if collection is none but kind is not none find all collections
        # matching THIS IS NOT YET IMPLEMENTED
        #
        if kinds and clouds:
            for _kind in kinds:
                for _cloud in clouds:
                    _collection = f"{_cloud}-{_kind}"
                    add(_collection)

        if collections:
            for _collection in collections:
                add(_collection)

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

    def find(self,
             collection=None,
             cloud=None,
             kind=None,
             query=None,
             attributes=None):
        """
        finds all names in the specified collections. The parameters,
        collection, cloud, and kind can all be Parameters that get expanded
        to lists. All names from all collections are merged into the result.

        With kwargs a search query on the names could be added.

        Example::

            cm = CmDatabase()
            for kind in ['vm', "image", "flavor"]:
                entries = cm.find(cloud="chameleon", kind=kind)
            print (entries)


            entries = cm.find(cloud="chameleon,azure", kind="vm")
            query = {"name": {'$regex': ".*Ubuntu.*"}}
            entries = cm.find(collection="chameleon-image", query=query)

        :param collection: The collections
        :param cloud: The clouds
        :param kind: The kinds
        :param query: A query applied to name
        :return:
        """
        MongoDBController().start_if_not_running()
        collections = Parameter.expand(collection)
        clouds = Parameter.expand(cloud)
        kinds = Parameter.expand(kind)
        result = []

        if not query:
            query = {}

        _attributes = {"_id": 0}

        if attributes:
            for a in attributes:
                _attributes[a] = 1

        def add(collection):
            col = self.db[collection]

            entries = col.find(
                query,
                _attributes)
            for entry in entries:
                result.append(entry)

        if kinds and clouds:
            for _kind in kinds:
                for _cloud in clouds:
                    _collection = f"{_cloud}-{_kind}"
                    add(_collection)

        if collections:
            for _collection in collections:
                add(_collection)
        return result

    # ok
    def find_ok(self, collection="cloudmesh", **kwargs):
        MongoDBController().start_if_not_running()
        col = self.db[collection]

        if len(kwargs) == 0:
            entries = col.find({}, {"_id": 0})
        else:
            entries = col.find(kwargs, {"_id": 0})

        # print ("KKKKK", kwargs)
        # print ("HHHH", entries.count())

        records = []
        for entry in entries:
            records.append(entry)
        return records

    @staticmethod
    def UPDATE(_entries, progress=True):
        cm = CmDatabase()
        r = cm.update(_entries, progress)
        cm.close_client()
        return r

    # ok
    def update(self, _entries, progress=True):
        MongoDBController().start_if_not_running()
        if type(_entries) == dict:
            entries = [_entries]
        else:
            entries = _entries

        if progress:
            bar = Bar('Cloudmesh Database Update', max=len(entries))

        result = []
        for entry in entries:
            if progress:
                bar.next()
            if 'cm' not in entry:
                print("UPDATE ERROR")
                VERBOSE(entry)
                raise ValueError("The cm attribute is not in the entry")
            entry['cm']['collection'] = "{cloud}-{kind}".format(**entry["cm"])

            # noinspection PyUnusedLocal
            try:
                self.col = self.db[entry['cm']['collection']]

                old_entry = self.col.find_one({"cm.kind": entry["cm"]["kind"],
                                               "cm.cloud": entry["cm"]["cloud"],
                                               "cm.name": entry["cm"]["name"]
                                               })

                if old_entry is not None:

                    cm = dict(old_entry['cm'])

                    cm.update(entry['cm'])
                    cm['modified'] = str(datetime.utcnow())

                    # entry['cm']['created'] = cm['created']
                    entry['cm'] = cm

                    post = self.col.replace_one(
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
                    self.col.insert_one(entry)

            except Exception as e:
                print()
                Console.error("uploading document\n{entry}\n-------\n\n".format(
                    entry=str(entry)))
                VERBOSE(e)
                pass
            result.append(entry)

        if progress:
            bar.finish()

        return result

    def alter(self, entries):
        MongoDBController().start_if_not_running()
        # for entry in entries:
        for entry in entries:
            try:
                # self.db["{cloud}-{kind}".format(**entry)].update(uniqueKeyVal,{'$set': keyvalToUpdate})
                entry['modified'] = str(datetime.utcnow())
                self.db["{cloud}-{kind}".format(**entry)].update(
                    {'cm': entry['cm']}, {'$set': entry})
            except Exception as e:
                Console.error("modifying document {entry}".format(
                    entry=str(entry)))
                pass
        return entries

    def exists(self, entries):
        """
        Check if entry exists in the database

        :param entries:
        :return:
        """
        MongoDBController().start_if_not_running()
        exist_status = []
        if type(entries) is dict:
            entries = [entries]
        for entry in entries:
            collection = self.db["{cloud}-{kind}".format(**entry)]
            status = collection.find(
                {'cm': {'$exists': entry['cm']}}).count() > 0
            exist_status.append(status)
        return exist_status

    # check
    def insert(self, d, collection="cloudmesh"):
        MongoDBController().start_if_not_running()
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

    # ok
    def delete(self, collection="cloudmesh", **kwargs):
        MongoDBController().start_if_not_running()
        col = self.db[collection]
        r = col.delete_many(kwargs)
        return r.deleted_count

    # ok
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
        MongoDBController().start_if_not_running()
        col = self.db[collection]
        col.drop()

    def importAsFile(self, data, collection, db):
        if collection in self.collections():
            self.clear(collection=collection)
            Console.msg(f"Collection {collection} dropped to be rewritten")
        MongoDBController().importAsFile(data, collection, db)
        # MongoDBController().start_if_not_running()
        # tmp_folder = path_expand('~/.cloudmesh/tmp')
        # if not os.path.exists(tmp_folder):
        #     os.makedirs(tmp_folder)
        # tmp_file = path_expand('~/.cloudmesh/tmp/tmp_import_file.json')
        # Console.msg("Saving the data to file ")
        # with open(tmp_file, 'w') as f:
        #     for dat in data:
        #         f.write(json.dumps(dat) + '\n')
        #
        # if collection in self.collections():
        #     self.clear(collection=collection)
        #     Console.msg(f"Collection {collection} dropped to be rewritten")
        # cmd = f'mongoimport --db {db} --collection {collection} ^ --authenticationDatabase admin --username {self.username} --password {self.password} ^ --drop --file {tmp_file}'
        #
        # Console.msg("Importing the saved data to database")
        # if platform.lower() =='win32':
        #     class disable_file_system_redirection:
        #         _disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
        #         _revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection
        #
        #         def __enter__(self):
        #             self.old_value = ctypes.c_long()
        #             self.success = self._disable(ctypes.byref(self.old_value))
        #
        #         def __exit__(self, type, value, traceback):
        #             if self.success:
        #                 self._revert(self.old_value)
        #     with disable_file_system_redirection():
        #         ssh = subprocess.Popen(cmd,
        #                                shell=True,
        #                                stdout=subprocess.PIPE,
        #                                stderr=subprocess.PIPE)
        # else:
        #     ssh = subprocess.Popen(cmd,
        #                            shell=True,
        #                            stdout=subprocess.PIPE,
        #                            stderr=subprocess.PIPE)
        # result = ssh.stdout.read().decode("utf-8")
        # print(result)

    def drop_database(self):
        """
        dropping cloudmesh database
        :return:
        """
        MongoDBController().start_if_not_running()
        self.client.drop_database(self.db)
