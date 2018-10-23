from cm4.vm_manager.providerABC import CloudProviderABC


class AWSProvider(CloudProviderABC):
    def __init__(self, config):
        pass

    def start(self):
        print("Starting the AWS cloud instance")

    def stop(self):
        pass

    def status(self):
        pass