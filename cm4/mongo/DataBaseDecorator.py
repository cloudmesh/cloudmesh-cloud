from cm4.mongo.mongoDB import MongoDB


class DatabaseUpdate:
    """
    Save the method's output to a MongoDB collection
    if the output is a dict or list of dicts.

    Example:

        @DatabaseUpdate("test-collection")
        def foo(x):
            return {"test": "hello"}
    """
    def __init__(self, collection=""):
        self.mongo = MongoDB()
        self.collection = collection

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            d = f(*args, **kwargs)

            if d is None:
                pass
            elif isinstance(d, list):
                self.mongo.save_list(self.collection, d)
            else:
                self.mongo.save_list(self.collection, [d])

            return d

        return wrapped_f
