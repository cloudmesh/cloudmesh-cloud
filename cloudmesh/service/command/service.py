from cloudmesh.common.Printer import Printer
from cloudmesh.configuration.Config import Config
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command


class ServiceCommand(PluginCommand):

    # noinspection PyUnusedLocal,PyBroadException
    @command
    def do_service(self, args, arguments):
        """
        ::

          Usage:
                service list

          Description:

              Lists the services in the yaml file

        """

        service_list = []

        entries = Config()["cloudmesh"]

        for kind in entries:
            try:
                services = entries[kind]
                for name in services:
                    service = services[name]
                    if 'cm' in service:
                        service['cm']['service'] = kind
                        service_list.append(service['cm'])
            except:
                pass
        print(Printer.write(service_list,
                            order=["label", "service", "active", "kind",
                                   "heading", "host", "version"]))
        return ""
