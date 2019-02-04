from cloudmesh.mongo.CmDatabase import CmDatabase
from pprint import pprint

class DatabaseUpdate:
    """
    Save the method's output to a MongoDB collection
    if the output is a dict or list of dicts.

    Example:

        @DatabaseUpdate("test-collection")
        def foo(x):
            return {"test": "hello"}
    """
    def __init__(self, collection="cloudmesh", replace=False):
        self.database = CmDatabase()
        self.replace = replace
        self.collection = collection

    def __call__(self, f):
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)

            r = self.database.update(result, collection=self.collection, replace=self.replace)

            return result
        return wrapper



