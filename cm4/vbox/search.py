import webbrowser

class search(object):

    def __init__(self):
        self.location = "https://app.vagrantup.com/boxes/search"
        self.open()

    def open(self, path=None):
        if path is not None:
            self.location = path

        webbrowser.open(self.location, new=1, autoraise=True)
