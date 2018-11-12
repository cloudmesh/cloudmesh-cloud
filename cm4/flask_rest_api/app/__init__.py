from flask import Flask
from flask_pymongo import PyMongo

from cm4.flask_rest_api.rest_config import Config

app = Flask(__name__)
app.config.from_object(Config)

mongo = PyMongo(app)
cloud = mongo.db.cloud

from cm4.flask_rest_api.app import routes