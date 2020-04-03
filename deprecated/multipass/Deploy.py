class Deploy:

    def __init__(self):
        self.operating_system = "unkown"
        #
        # how do you find the OS?
        #
        # IMPLEMENT.
        #
        #

    def install(self):
        if self.operating_system == "windows":
            self._install_on_windows()
        elif self.operating_system == "darwin":
            self._install_on_osx()
        elif self.operating_system == "ubuntu":
            self._install_on_ubuntu()
        else:
            # theer could be different
            # methods on different linux versions.
            raise NotImplementedError

    def _install_on_windows(self):
        # see https://multipass.run/docs/installing-on-windows
        raise NotImplementedError

    def _install_on_osx(self):
        # see https://multipass.run/docs/installing-on-macos
        raise NotImplementedError

    def _install_on_ubuntu(self):
        # see https://multipass.run/docs/installing-on-linux
        raise NotImplementedError
