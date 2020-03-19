from textwrap import dedent

from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.configuration.Config import Config
from cloudmesh.register.Entry import Entry


class Register(object):

    def __init__(self):
        print("init {name}".format(name=self.__class__.__name__))

    @staticmethod
    def list_all():
        config = Config()
        config_service = config["cloudmesh"]

        service_list = []

        for item in config_service:
            if item in "cloud storage volume data cluster":
                list_item = {}
                kinds = []
                for sub_item in config_service[item]:
                    kinds.append(sub_item)

                list_item["service"] = item
                list_item["kind"] = kinds

                service_list.append(list_item)

        Console.info("Services to be registered")
        print(Printer.flatwrite(service_list,
                                sort_keys=["service"],
                                order=["service", "kind"],
                                header=["Service", "Supported Kind"],
                                output="table",
                                humanize=None)
              )

        return service_list

        # print(config_service);

        return ""

    @staticmethod
    def print_sample(service=None, kind=None):
        if not kind or not service:
            Console.error("Both kind and service required to print sample.")
            return

        provider = Register.get_provider(service=service, kind=kind)

        if provider is None:
            Console.error("No suitable provider found.")
            return

        sample = provider.sample

        if len(sample) >= 1:
            Console.info(f"Sample for service={service} kind={kind}")

            print(dedent(sample))

            Console.error("The following attributes are not defined")
            print()
            keys = Register.get_sample_variables(sample)

            print("    " + "\n    ".join(sorted(keys)))
            print()

        return ""

    @staticmethod
    def print_kinds(service=None, kind=None):
        if not service:
            Console.error("Service required to print kind.")
            return

        provider = Register.get_provider(service=service, kind=kind)

        if provider is None:
            Console.error("No suitable provider found.")
            return

        kinds = provider.get_kind()

        Console.info(f"Kind for service={service}")
        print()
        print("    " + "\n    ".join(sorted(kinds)))
        print()

        return ""

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

                if kind is None:
                    from cloudmesh.compute.vm.Provider import Provider
                else:
                    from cloudmesh.compute.vm.Provider import Provider as P
                    Provider = P.get_provider(kind)

            elif service == 'storage':

                from cloudmesh.storage.Provider import Provider as P
                if kind is None:
                    from cloudmesh.storage.Provider import Provider
                else:
                    Provider = P.get_provider(kind)

            elif service == 'volume':

                from cloudmesh.volume.Volume import Provider as P
                Provider = P.get_provider(kind)

        except Exception as e:
            Console.error(
                f"Registration failed kind={kind} and service={service}")
            print(e)
            return None

        if Provider is None:
            Console.error(
                f"Registration no Provider found for kind={kind} and service={service}")
            return None

        # print("Provider:", Provider)

        p = Provider

        return p

    @staticmethod
    def get_sample_variables(sample):
        keys = set()
        lines = sample.splitlines()
        for line in lines:
            if "{" in line and "}" in line:
                name = (line.split("{", 1)[1]).split("}", 1)[0]
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
        except Exception as e:
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

    @staticmethod
    def remove(service, name):
        removed_item = None
        try:
            # Update the google cloud section of cloudmesh.yaml config file.
            config = Config()
            config_service = config["cloudmesh"][service]

            if name in config_service:
                removed_item = config_service.pop(name, None)
                config.save()

                Console.ok(
                    f"Removed {name} from {service} service.")

            else:
                Console.warning(
                    f"{name} is not registered for cloudmesh.{service}")

        except Exception as se:
            Console.error(f"Error removing {service}-{name} :: {se}")

        return removed_item

    @staticmethod
    def update(provider, kind, service, name, attributes):
        try:
            sample = Register.get_sample(provider,
                                         kind,
                                         service,
                                         name,
                                         attributes)

            if sample is None:
                Console.error("The sample is not fully filled out.")
                return ""

            # Add the entry into cloudmesh.yaml file.
            config = Config()
            config_path = config.location.config()

            Entry.add(entry=sample,
                      base=f"cloudmesh.{service}",
                      path=config_path)

            Console.ok(
                f"Registered {service} service for {kind}"
                f" provider with name {name}.")

        except Exception as se:
            Console.error(f"Error updating {service}-{name} :: {se}")
        return ""
