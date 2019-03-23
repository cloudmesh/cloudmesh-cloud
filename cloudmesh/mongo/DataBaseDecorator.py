from datetime import datetime

from cloudmesh.management.configuration.name import Name
from cloudmesh.mongo.CmDatabase import CmDatabase


class DatabaseUpdateOld:
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
                result["modified"] = str(datetime.utcnow())
                if "created" not in result:
                    result["created"] = result["modified"]
                # noinspection PyUnusedLocal
                r = self.database.update(result,
                                         collection=self.collection,
                                         replace=self.replace)

            return result

        return wrapper


class DatabaseAddOld:
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
            result["created"] = result["modified"] = str(datetime.utcnow())
            self.name.incr()

            if result is not None:
                result["created"] = result["modified"] = str(datetime.utcnow())
                # noinspection PyUnusedLocal
                r = self.database.update(result, collection=self.collection,
                                         replace=self.replace)

            return result

        return wrapper


class DatabaseUpdate:
    """
    Prints the dict of the result but does not add it to the DB

    Example:

        @DatabaseUpdate("test-collection")
        def foo(x):
            return {"test": "hello"}
    """

    # noinspection PyUnusedLocal
    def __init__(self, **kwargs):
        self.database = CmDatabase()

    def __call__(self, f):
        def wrapper(*args, **kwargs):
            current = f(*args, **kwargs)
            if type(current) == dict:
                current = [current]

            result = self.database.update(current)

            return result

        return wrapper
