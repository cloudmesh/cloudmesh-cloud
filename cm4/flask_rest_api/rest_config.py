from cm4.configuration.config import Config


class RestConfig(object):
    config = Config().get('data.mongo')
    MONGO_URI = "mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DBNAME}".format(**config)
