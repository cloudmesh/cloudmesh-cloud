from cloudmesh.common.parameter import Parameter
from cloudmesh.common.console import Console
from cloudmesh.management.configuration.config import Active


class Arguments(object):

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
            Console.error("you need to specify a vm")
            return None
        else:
            return Parameter.expand(names)

    @staticmethod
    def name_loop(names, label, f):
        names = Arguments.get_names(arguments, variables)
        for name in names:
            Console.msg("{label} {name}".format(label=label, name=name))
            # r = f(name)