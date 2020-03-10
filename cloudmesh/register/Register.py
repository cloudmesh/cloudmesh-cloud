from cloudmesh.common.console import Console

class Register(object):

    def __init__(self):
        print("init {name}".format(name=self.__class__.__name__))

    @staticmethod
    def get_provider(service, kind):
        """
        Method to import the provider based on the service and kind.
        :param service: Type of the service e.g. compute or storage etc.
        :param kind: Name of the cloud e.g. google, azure, aws etc.
        :return: Provider class
        """
        try:
            if service == 'compute' or service == 'cloud':

                from cloudmesh.compute.vm.Provider import Provider as P


                if kind == 'openstack':
                    from cloudmesh.openstack.compute.Provider import Provider
                elif kind == 'azure':
                    from cloudmesh.azure.compute.Provider import Provider
                elif kind == 'aws':
                    from cloudmesh.aws.compute.Provider import Provider
                elif kind == 'oracle':
                    from cloudmesh.oracle.compute.Provider import Provider
                elif kind == 'google':
                    from cloudmesh.google.compute.Provider import Provider
                else:
                    Console.error(
                        f"No suitable provider found for {kind} and {service}")
                    return None

            elif service == 'storage':

                if kind == 'openstack':
                    from cloudmesh.openstack.storage.Provider import Provider
                elif kind == 'azure':
                    from cloudmesh.storage.azure.Provider import Provider
                elif kind == 'aws':
                    from cloudmesh.storage.aws.Provider import Provider
                elif kind == 'oracle':
                    from cloudmesh.oracle.compute.Provider import Provider
                elif kind == 'google':
                    from cloudmesh.google.storage.Provider import Provider
                else:
                    Console.error(
                        f"No suitable provider found for {kind} and {service}")
                    return None

            elif service == 'volume':

                from cloudmesh.volume.Volume import Provider
                p = Provider ()
                return p.get(kind)

            else:
                Console.error(f"Invalid {service} provided.")
                return None
        except:
            Console.error(f"Registration failed {service} and {kind}")
            return None

        p = Provider

        return p

    @staticmethod
    def get_sample(provider, kind, service, name, attributes):

        # Default replacements.
        replacements = {'name': name,
                        'service': service,
                        "kind": kind}

        # Add the attributes to the dict.
        for attribute in attributes:
            key, value = attribute.split("=")
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
            Console.error(f"Value for {e} is not specified")
            sample = None

        return sample
