from cloudmesh.common.console import Console

class Register(object):

    def __init__(self):
        print("init {name}".format(name=self.__class__.__name__))

    @staticmethod
    def get_provider(kind=None, service=None):
        """
        Method to import the provider based on the service and kind.

        :param service: Type of the service e.g. compute or storage, volume
        :param kind: Name of the cloud e.g. google, azure, aws etc.
        :return: Provider class
        """
        Provider = None

        try:
            if service in ['compute', 'cloud']:

                from cloudmesh.compute.vm.Provider import Provider as P
                Provider = P.get_provider(kind)

            elif service == 'storage':

                from cloudmesh.compute.vm.Provider import Provider as P
                Provider = P.get_provider(kind)

            elif service == 'volume':

                from cloudmesh.volume.Volume import Provider as P
                Provider = P.get_provider(kind)

        except Exception as e:
            Console.error(f"Registration failed kind={kind} and service={service}")
            print(e)
            return None

        if Provider is None:
            Console.error(f"Registration no Provider found for kind={kind} and service={service}")
            return None

        print("Provider:", Provider)

        p = Provider

        return p

    @staticmethod
    def get_sample_variables(sample):
        keys = set()
        lines = sample.splitlines()
        for line in lines:
            if "{" in line and "}" in line:
                name = (line.split("{",1)[1]).split("}",1)[0]
                keys.add(name)
        return list(keys)


    @staticmethod
    def get_sample(provider, kind, service, name, attributes):

        # Default replacements.
        replacements = {'name': name,
                        'service': service,
                        "kind": kind}

        # Add the attributes to the dict.
        for key, value in attributes.items():
            replacements[key] = value

        try:
            # Extract the sample from Provider.
            sample = provider.sample
        except:
            Console.error(f"Can not find the sample in the Provider")
            return ""

        try:
            # Format the sample by replacing the attributes.
            sample = sample.format(**replacements)

        except KeyError as e:

            print(sample)

            Console.error(f"Value for {e} is not specified")
            sample = None

        return sample
