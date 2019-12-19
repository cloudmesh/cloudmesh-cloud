class Register(object):

    def __init__(self):
        print("init {name}".format(name=self.__class__.__name__))

    def aws(self, filename):
        #
        # do import
        # have a uniform entry sample in each provider
        # verify against entry
        print("register", filename)
        raise NotImplementedError

    def azure(self, filename):
        print("register", filename)

        raise NotImplementedError

    def google(self, filename):
        print("register", filename)

        raise NotImplementedError

    def chameleon(self, filename):
        print("register", filename)

        raise NotImplementedError
