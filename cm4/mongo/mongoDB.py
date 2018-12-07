from pymongo import MongoClient
import urllib.parse
from cm4.configuration.config import Config


class MongoDB(object):

    def __init__(self, host, username, password, port):
        self.database = Config().data["cloudmesh"]["data"]["mongo"]["MONGO_DBNAME"]
        self.host = host
        self.password = urllib.parse.quote_plus(password)
        self.username = urllib.parse.quote_plus(username)
        self.port = port
        self.client = None
        self.db = None
        self.connect_db()

    def set_port(self, port):
        """
        set port
        :param port:
        """
        self.port = port

    def set_username(self, username):
        """
        set username
        :param username:
        """
        self.username = urllib.parse.quote_plus(username)

    def set_password(self, password):
        """
        set password
        :param password:
        """
        self.password = urllib.parse.quote_plus(password)

    def connect_db(self):
        """
        connect to database
        """
        self.client = MongoClient('mongodb://%s:%s@%s:%s' % (self.username, self.password, self.host, self.port))
        self.db = self.client[self.database]

    def insert_config_document(self, document):
        """
        insert document to config collection
        :param document:
        :return: id of document
        """
        cm = self.db['config']
        post_id = cm.insert_one(document).inserted_id
        return post_id

    def insert_cloud_document(self, document):
        """
        insert document to cloud collection
        :param document:
        :return: id of document
        """
        cm = self.db['cloud']
        print(cm)
        post_id = cm.insert_one(self.var_to_json(document)).inserted_id
        return post_id

    def insert_status_collection(self, document):
        """
        insert document to status collection, the collection contains the information about each node
        :param document:
        :return: id of document
        """
        status = self.db['status']
        post_id = status.insert_one(document).inserted_id
        return post_id

    def insert_job_collection(self, document):
        """
        insert document to job collection, the collection contains the information about job running in node
        :param document:
        :return: id of document
        """
        job = self.db['job']
        post_id = job.insert_one(document).inserted_id
        return post_id

    def insert_group_collection(self, document):
        """
        insert document to group collection, the collection contains the information about created group
        :param document:
        :return: id of document
        """
        group = self.db['group']
        post_id = group.insert_one(document).inserted_id
        return post_id

    def update_document(self, collection_name, key, value, info):
        """
        update document
        :param collection_name: the name of the collection
        :param key: the key that we find the document
        :param value: the value that we find the document
        :param info: the update information
        :return:
        """
        collection = self.db[collection_name]
        result = collection.update_one({key: value}, {'$set': self.var_to_json(info)}).acknowledged
        return result

    def find_document(self, collection_name, key, value):
        """
        find the document in a collection
        :param collection_name: collection name, like 'default', 'job' ....
        :param key: search key
        :param value: search value
        :return: the document which match the key and value
        """
        collection = self.db[collection_name]
        document = collection.find_one({key: value})
        return document

    def find(self, collection_name, key=None, value=None):
        """
        find all the documents in a collection.
        If no key is specified, all the documents are returned.
        :param collection_name: collection name, like 'default', 'job' ....
        :param key: search key
        :param value: search value
        :return: the documents which matches the key and value
        """
        collection = self.db[collection_name]
        if key is None:
            documents = collection.find()
        else:
            documents = collection.find({key: value})
        return documents

    def delete_document(self, collection_name, key, value):
        """
        delete the document
        :param collection_name: collection name, like 'default', 'job' ....
        :param key: search key
        :param value: search value
        :return: the deleted document
        """
        collection = self.db[collection_name]
        old_document = collection.find_one_and_delete({key: value})
        return old_document

    def db_command(self, command):
        """
        issue command string against mongoDB console
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

    def test_db_connection(self):
        """
        test mongodb correspondent db connection
        :return:
        """
        return self.db_command("serverStatus")

    @staticmethod
    def status_document(instance_name, status, job_id, history):
        """
        create status document
        :param instance_name: the name of vm
        :param status: the status of the vm, processing or No job
        :param job_id: the job document id
        :param history: the list of job document ids
        :return:
        """
        document = {'id': instance_name,
                    'status': status,
                    'currentJob': job_id,
                    'history': history}
        return document

    @staticmethod
    def job_document(name, status, input_info, output_info, commands, description='Null'):
        """
        create job document
        :param name:
        :param status:
        :param input_info:
        :param output_info:
        :param commands:
        :param description:
        :return:
        """
        document = {'name': name,
                    'status': status,
                    'input': input_info,
                    'output': output_info,
                    'description': description,
                    'commands': commands}
        return document

    @staticmethod
    def group_document(cloud, name, size, list_vms):
        """
        create group document
        :param cloud:
        :param name:
        :param size:
        :param list_vms:
        :return:
        """
        document = {'cloud': cloud,
                    'name': name,
                    'size': size,
                    'vms': list_vms}
        return document

    def var_to_json(self, document):
        new = dict()
        for key in document.keys():
            if isinstance(document[key], dict):
                new.update({key: self.var_to_json(document[key])})
            elif isinstance(document[key], list):
                temp = []
                for item in document[key]:
                    if isinstance(item, dict):
                        temp.append(self.var_to_json(item))
                    elif isinstance(item, str):
                        temp.append(item)
                    elif isinstance(item, int):
                        temp.append(item)
                    elif isinstance(item, list):
                        temp.append(item)
                new.update({key: temp})
            elif isinstance(document[key], str):
                new.update({key: document[key]})
            elif isinstance(document[key], int):
                new.update({key: document[key]})

        return new

    def close_client(self):
        """
        close the connection to mongodb
        """
        self.client.close()
