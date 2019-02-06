from cloudmesh.mongo.CmDatabase import CmDatabase
from pprint import pprint
from cloudmesh.management.configuration.name import Name
from datetime import datetime
from cloudmesh.common.util import banner


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

            if result is not None:
                result["updated"] = str(datetime.utcnow())
                if "created" not in result:
                    result["created"] = result["updated"]
                r = self.database.update(result, collection=self.collection, replace=self.replace)

            return result

        return wrapper


class DatabaseAdd:
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
        self.name = Name()

    def __call__(self, f):
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            result["cmid"] = str(self.name)
            result["cmcounter"] = str(self.name.counter)
            result["created"] = result["updated"] = str(datetime.utcnow())
            self.name.incr()

            if result is not None:
                result["created"] = result["updated"] = str(datetime.utcnow())
                r = self.database.update(result, collection=self.collection, replace=self.replace)

            return result

        return wrapper


class DatabasePrint:
    """
    Prints the dict of the result but does not add it to the DB

    Example:

        @DatabaseUpdate("test-collection")
        def foo(x):
            return {"test": "hello"}
    """

    def __init__(self, collection="cloudmesh", replace=False):
        self.name = Name()

    def __call__(self, f):
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            result["cmid"] = str(self.name)
            result["cmcounter"] = str(self.name.counter)
            result["created"] = result["updated"] = str(datetime.utcnow())

            banner(result["cmid"], c=".")

            if result is not None:
                result["created"] = result["updated"] = str(datetime.utcnow())
                pprint(result)
            else:
                print(None)
            print(70 * ".")

            return result

        return wrapper
