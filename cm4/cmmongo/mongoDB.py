from pymongo import MongoClient
from cm4.abstractclass.DatabaseManagerABC import DatabaseManagerABC
import urllib.parse


class MongoDB(DatabaseManagerABC):
    # haven't tested it

    def __init__(self):
        self.database = 'cloudmesh'
        self.password = None
        self.username = None
        self.port = None
        self.client = None
        self.db = None

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
        self.username = urllib.parse.quote_plus (username)

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
        self.client = MongoClient ('mongodb://%s:%s@127.0.0.1:%s' % (self.username, self.password, self.port))
        self.db = self.client[self.database]

    def insert_default_collection(self, document):
        """
        insert document to default collection
        :param document:
        :return: id of document
        """
        cm = self.db['default']
        post_id = cm.insert_one(document).inserted_id
        return post_id

    def insert_cloud_document(self, document):
        """
        insert document to cloud collection
        :param document:
        :return: id of document
        """
        cm = self.db['cloud']
        post_id = cm.insert_one(document).inserted_id
        return post_id

    def insert_chameleon_document(self, document):
        """
        insert document to chameleon collection
        :param document:
        :return: id of document
        """
        cm = self.db['chameleon']
        post_id = cm.insert_one (document).inserted_id
        return post_id

    def insert_data_document(self, document):
        """
        insert document to data collection
        :param document:
        :return: id of document
        """
        cm = self.db['data']
        post_id = cm.insert_one (document).inserted_id
        return post_id

    def insert_cluster_collection(self, document):
        """
        insert document to cluster collection
        :param document:
        :return: id of document
        """
        instance = self.db['instance']
        post_id = instance.insert_one(document).inserted_id
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

    def update_document(self, collection_name, ID, info):
        """
        update document in any collection
        :param collection_name: collection name, like 'default', 'job' ....
        :param ID: the document id
        :param info: updated information (key-value)
        :return: True/False
        """
        collection = self.db[collection_name]
        result = collection.update_one({'_id': ID}, {'$set': info}).acknowledged
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
        document = collection.find({key: value})
        return document

    def delete_document(self, collection_name, ID):
        """
        delete the document from collection
        :param collection_name: collection name, like 'default', 'job' ....
        :param ID: document id
        :return: the deleted document
        """
        collection = self.db[collection_name]
        old_document = collection.find_one_and_delete({'_id': ID})
        return old_document


    @staticmethod
    def cluster_document(label, cloud, name, os='Null', cpu='Null', memory='Null',
                          storage='Null', address='Null', credential_id='Null', credential_key='Null', group_id='Null'):
        """
        create cluster document
        :param label:
        :param cloud:
        :param name:
        :param os:
        :param cpu:
        :param memory:
        :param storage:
        :param address:
        :param credential_id:
        :param credential_key:
        :param group_id:
        :return:
        """
        document = {'label': label,
                    'cloud': cloud,
                    'name': name,
                    'spec': {'os': os,
                             'cpu': cpu,
                             'memory': memory,
                             'storage': storage},
                    'address': address,
                    'credential': {'id': credential_id,
                                   'key': credential_key},
                    'group': group_id
                    }
        return document

    @staticmethod
    def status_document(instance_id, status, job_id, history):
        """
        create status document
        :param instance_id:
        :param status:
        :param job_id:
        :param history:
        :return:
        """
        document = {'_id': instance_id,
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

    def close_client(self):
        """
        close the connection to mongodb
        """
        self.client.close()





