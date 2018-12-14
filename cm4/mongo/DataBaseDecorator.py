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
    def __init__(self, collection="cloud", result_mapper=None):
        self.mongo = MongoDB()
        self.collection = collection
        self.result_mapper = result_mapper

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            result = f(*args, **kwargs)
            is_list = True

            if result is None:
                return None
            elif not isinstance(result, list):
                result = [result]
                is_list = False

            if self.result_mapper:
                mapper = getattr(args[0], self.result_mapper.__name__)
                result = list(map(mapper, result))

            self.mongo.save_list(self.collection, result)

            return result if is_list else result[0]

        return wrapped_f
