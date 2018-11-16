# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 13:48:09 2018

@author: Wu
"""

import pprint
from flask import Flask, request, jsonify
from cm4.cmmongo.mongoDB import MongoDB
from cm4.vm.Vm import Vm

app = Flask(__name__)
app.config['ENV']='development'
app.config['JSONIFY_PRETTYPRINT_REGULAR']=True


db = MongoDB('host','user','password','port')
db.connect_db()


@app.route('/')
def hello_world():
    return "test!"


@app.route('/list')
def list():
    """
    return status of instnace. If given `cloud`, query cloud platform; otherwise query db.
    """
    cloud = request.args.get('cloud')
    if cloud:
        rep = Vm(cloud).list()
        return 'No node is found on {}!\n'.format(cloud) if not rep else \
                jsonify(**{'records' : [db.var_to_json(x.__dict__) for x in rep]})
    else:
        return jsonify(**{'records': [db.var_to_json(x) for x in db.db['cloud'].find()]})


@app.route('/info')
def info():
    name = request.args.get('name')
    cloud = request.args.get('cloud')
    if cloud: # query cloud, return node
        rep = Vm(cloud).info(name)
        return 'Node {} not found!\n'.format(name) if not rep else jsonify(**db.var_to_json(rep.__dict__)) 
    else:     # query db, return dco
        query = db.find_document('cloud','name', name)
        return 'Node {} not found!\n'.format(name) if not query else jsonify(**db.var_to_json(query)) 


@app.route('/start')
def start():
    name = request.args.get('name')
    cloud = request.args.get('cloud')
    rep = Vm(cloud).start(name)
    return jsonify(**db.var_to_json(rep)) 


@app.route('/stop')
def stop():
    name = request.args.get('name')
    cloud = request.args.get('cloud')
    rep = Vm(cloud).stop(name)
    return jsonify(**db.var_to_json(rep)) 


