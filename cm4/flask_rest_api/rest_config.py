class Config(object):
    MONGO_DBNAME = "cloudmesh"
    MONGO_HOST = "127.0.0.1"
    MONGO_PORT = "27017"
    MONGO_USERNAME = "admin"
    MONGO_PASSWORD = "admin"
    MONGO_URI = "mongodb://" + MONGO_USERNAME + ":" + MONGO_PASSWORD + "@" + MONGO_HOST + ":" + MONGO_PORT + "/" + MONGO_DBNAME
