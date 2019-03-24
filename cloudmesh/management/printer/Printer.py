class Printer(object):

    def __init__(self, sort_keys=None, order=None, header=None):
        self.sort_keys = sort_keys
        self.order = order
        self.header = header

    def print(self, d, format='table'):
        print(self.value(d,format=format))

    def value(self, d, format='table'):
        return Printer.flatwrite(
            d,
            sort_keys=self.keys,
            order=self.order,
            header=self.header
            )
