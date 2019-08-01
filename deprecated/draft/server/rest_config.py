from cloudmesh.configuration.Config import Config


class RestConfig(object):
    config = Config().data["cloudmesh"]
    MONGO_HOST = config["data"]["mongo"]["MONGO_HOST"]
    MONGO_USERNAME = config["data"]["mongo"]["MONGO_USERNAME"]
    MONGO_PASSWORD = config["data"]["mongo"]["MONGO_PASSWORD"]
    MONGO_PORT = config["data"]["mongo"]["MONGO_PORT"]
    MONGO_DBNAME = config["data"]["mongo"]["MONGO_DBNAME"]

    # MONGO_DBNAME = config.get("data.mongo.MONGO_DBNAME")
    # MONGO_HOST = config.get("data.mongo.MONGO_HOST")
    # MONGO_PORT = config.get("data.mongo.MONGO_PORT")
    # MONGO_USERNAME = config.get("data.mongo.MONGO_USERNAME")
    # MONGO_PASSWORD = config.get("data.mongo.MONGO_PASSWORD")
    MONGO_URI = "mongodb://" + MONGO_USERNAME + ":" + MONGO_PASSWORD + "@" + MONGO_HOST + ":" + MONGO_PORT + "/" + MONGO_DBNAME
    # TODO:
    # MONGO_URI = "mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DBNAME}".format(**data.mongo)
