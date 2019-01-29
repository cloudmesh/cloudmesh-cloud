from flask import Flask
from flask_pymongo import PyMongo

from cloudmesh.server.rest_config import RestConfig

app = Flask(__name__)
app.config.from_object(RestConfig)

mongo = PyMongo(app)
cloud = mongo.db.cloud

#
# TODO: WHY IS THIS NOT ON THE TOP
#

from cloudmesh.server.app import routes
