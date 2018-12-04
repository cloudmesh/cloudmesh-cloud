from cm4.configuration.config import Config


class RestConfig(object):
    config = Config()
    MONGO_DBNAME = config.get("data.mongo.MONGO_DBNAME")
    MONGO_HOST = config.get("data.mongo.MONGO_HOST")
    MONGO_PORT = config.get("data.mongo.MONGO_PORT")
    MONGO_USERNAME = config.get("data.mongo.MONGO_USERNAME")
    MONGO_PASSWORD = config.get("data.mongo.MONGO_PASSWORD")
    MONGO_URI = "mongodb://" + MONGO_USERNAME + ":" + MONGO_PASSWORD + "@" + MONGO_HOST + ":" + MONGO_PORT + "/" + MONGO_DBNAME+ MONGO_USERNAME + ":" + MONGO_PASSWORD + "@" + MONGO_HOST + ":" + MONGO_PORT + "/" + MONGO_DBNAME