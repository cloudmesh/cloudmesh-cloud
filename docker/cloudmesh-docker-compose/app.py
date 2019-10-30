from bson.json_util import dumps
from flask import Flask, Response
from flask_pymongo import PyMongo
from pymongo.errors import ServerSelectionTimeoutError

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://mongo:27017/test-database"
mongo = PyMongo(app)


def query_mongodb():
    try:
        server_status_result = mongo.cx.testdb.command("serverStatus")
        return server_status_result
    except ServerSelectionTimeoutError as e:
        return e


@app.route('/')
def home():
    results = query_mongodb()
    js = dumps(results)
    return Response(js, status=200, mimetype='application/json')
