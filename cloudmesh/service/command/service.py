from cloudmesh.common.console import Console
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.management.configuration.config import Config
from pprint import pprint
from cloudmesh.common.FlatDict import flatten
import oyaml as yaml
from cloudmesh.common.util import banner
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand
from cloudmesh.common.Printer import Printer


class ServiceCommand(PluginCommand):

    # noinspection PyUnusedLocal
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

        all = Config()["cloudmesh"]

        for kind in all:
            try:
                services = all[kind]
                for name in services:
                    service = services[name]
                    if 'cm' in service:
                        service['cm']['service'] = kind
                        service_list.append(service['cm'])
            except:
                pass
        print(Printer.write(service_list,
                            order=["label", "service", "active", "kind", "heading", "host", "version"]))
        return ""
