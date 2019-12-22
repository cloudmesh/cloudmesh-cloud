from cloudmesh.common.console import Console
from cloudmesh.common.parameter import Parameter
from cloudmesh.configuration.Config import Active


class Arguments(object):

    @staticmethod
    def expand(arguments, *keys):
        """
        expands all entries in arguments identified by keys

        :param arguments: list of arguments
        :param keys: the keys that locate entries in arguments that are expanded
        :return: the expanded arguments. it is now a dict of lists
        """

        for key in keys:
            if key in arguments:
                entry = arguments[key]
                if entry:
                    if type(entry) == str:
                        entry = Parameter.expand(entry)
        return arguments

    @staticmethod
    def get_cloud_and_names(label, arguments, variables):
        names = []
        clouds = []

        if arguments["--cloud"]:
            clouds = Arguments.get_clouds(arguments, variables)
        else:
            clouds = Arguments.get_clouds(arguments, variables)

        names = Arguments.get_names(arguments, variables)

        return clouds, names

    @staticmethod
    def get_clouds(arguments, variables):

        clouds = arguments["cloud"] or arguments["--cloud"] or variables[
            "cloud"]
        if "active" == clouds:
            active = Active()
            clouds = active.clouds()
        else:
            clouds = Parameter.expand(clouds)

        if clouds is None:
            Console.error("you need to specify a cloud")
            return None

        return clouds

    @staticmethod
    def get_names(arguments, variables):
        names = arguments.get("NAME") or arguments.get(
            "NAMES") or arguments.get(
            "--name") or variables["vm"]
        # TODO: bug this only works for vm, but not images and so on
        if names is None:
            # this is a temporary patch for "image list --cloud=XX --refresh" so not to print the error
            if (arguments.cloud and arguments.refresh and arguments.list):
                return None
            Console.error("you need to specify a vm")
            return None
        else:
            return Parameter.expand(names)

    @staticmethod
    def name_loop(names, label, f):
        raise NotImplementedError
        names = Arguments.get_names(arguments, variables)
        for name in names:
            Console.msg("{label} {name}".format(label=label, name=name))
            # r = f(name)

    @staticmethod
    def get_attribute(attribute, arguments, variables):
        value = arguments[attribute] or arguments[f"--{attribute}"]
        if value is None:
            Console.error(f"you need to specify an `{attribute}")
            return None
        else:
            return value

    @staticmethod
    def get_flavor(arguments, variables):
        return Arguments.get_attribute("flavor", arguments, variables)

    @staticmethod
    def get_image(arguments, variables):
        return Arguments.get_attribute("image", arguments, variables)

    @staticmethod
    def get_command(arguments, variables):
        command = arguments["command"] or arguments["--command"]
        # if command is None:
        #    Console.error("you need to specify a command")
        #   return None
        # else:
        return command

    @staticmethod
    def get_commands(label, arguments, variables):
        #
        # TODO: why are onp all commands looking for clouds and names, likely a bug
        #
        names = []
        if label in ["images", "flavors", "list"]:
            clouds = Arguments.get_clouds(arguments, variables)
            return clouds
        if "boot" == label:
            clouds = Arguments.get_clouds(arguments, variables)
            names = Arguments.get_names(arguments, variables)
            image = Arguments.get_image(arguments, variables)
            flavor = Arguments.get_flavor(arguments, variables)
            return clouds, names, image, flavor
        if label in ["stop", "start", "delete"]:
            clouds = Arguments.get_clouds(arguments, variables)
            names = Arguments.get_names(arguments, variables)
            return clouds, names
        if "ssh" == label:
            clouds = Arguments.get_clouds(arguments, variables)
            names = Arguments.get_names(arguments, variables)
            command = Arguments.get_command(arguments, variables)
            return clouds, names, command
        return names
