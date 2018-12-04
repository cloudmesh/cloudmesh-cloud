from flask import Flask
from flask_pymongo import PyMongo

from cm4.flask_rest_api.rest_config import RestConfig

app = Flask(__name__)
app.config.from_object(RestConfig)

mongo = PyMongo(app)
cloud = mongo.db.cloud

#
# TODO: WHY IS THIS NOT ON THE TOP
#
from cm4.flask_rest_api.app import routes
