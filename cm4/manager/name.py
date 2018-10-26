class Name(object):

    #possibly move this to configuration
    
    def __init__(self):
        self.counter=0 # n sets and gets counter
        self.schema= "{experiment}-{group}={user}-{counter}" # default schema
        self.name =self._current()
        
    def incr():
        self.counter = self.counter + 1
        # store the counter in the yaml file so we can reuse it between sessions
    
    def set(self, schema):
        self.schema = schema

    def get(self, **knargs):
        # if verify passes continue als through exception
        self.incr()
        if len(knarg) = 0:
            # no parameters passed, retn one with counter increased
        #named args as defined in schema
        pass
    
    def verify(**knargs, schema):
        # verifies if kargs are defined returns tru/false
        pass

    def _current(self):
        # returns current name without increasing the counter
        #we have two ways to get the name
        #Name.current

    def load(self):
        # reads the counter form the yaml file

`
