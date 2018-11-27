from flask import Flask, request, jsonify
from cm4.cmmongo.mongoDB import MongoDB
from cm4.vm.Vm import Vm
from cm4.configuration.config import Config


config = Config()
db = MongoDB(config.get('data.mongo.MONGO_DBNAME'),
             config.get('data.mongo.MONGO_USERNAME'),
             config.get('data.mongo.MONGO_PASSWORD'),
             config.get('data.mongo.MONGO_PORT'))
db.connect_db()


def vm_list():
    cloud = request.args.get('cloud')
    if cloud:
        rep = Vm(cloud).list()
        return 'No node is found on {}!\n'.format(cloud) if not rep else \
               jsonify(**{'records': [db.var_to_json(x.__dict__) for x in rep]})
    else:
        return jsonify(**{'records': [db.var_to_json(x) for x in db.db['cloud'].find()]})

