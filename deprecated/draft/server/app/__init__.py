from flask import Flask
from flask_pymongo import PyMongo

from deprecated.draft.server import RestConfig

app = Flask(__name__)
app.config.from_object(RestConfig)

mongo = PyMongo(app)
cloud = mongo.db.cloud

#
# TODO: WHY IS THIS NOT ON THE TOP
#

from deprecated.draft.server.app import routes
