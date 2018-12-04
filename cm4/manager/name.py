class Name(object):

    # possibly move this to configuration

    def __init__(self):
        self.counter = 0  # n sets and gets counter
        self.schema = "{experiment}-{group}={user}-{counter}"  # default schema
        self.name = self._current()

    def incr(self):
        self.counter = self.counter + 1
        # store the counter in the yaml file so we can reuse it between sessions

    def set(self, schema):
        self.schema = schema

    def get(self, **kwargs):
        # if verify passes continue als through exception
        self.incr()
        if len(kwargs) == 0:
            # no parameters passed, retn one with counter increased
            # named args as defined in schema
            pass

    def verify(schema, **knargs):
        # verifies if kargs are defined returns tru/false
        pass

    def _current(self):
        # returns current name without increasing the counter
        # we have two ways to get the name
        # Name.current
        pass

    def load(self):
        # reads the counter form the yaml file
        pass
