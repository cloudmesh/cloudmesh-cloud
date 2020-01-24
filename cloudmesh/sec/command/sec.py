from pprint import pprint

from cloudmesh.common.Printer import Printer
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.variables import Variables

from cloudmesh.secgroup.Secgroup import Secgroup, SecgroupRule
from cloudmesh.secgroup.Secgroup import SecgroupExamples
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters
from cloudmesh.common.debug import VERBOSE
from cloudmesh.compute.vm.Provider import Provider
import sys


class SecCommand(PluginCommand):

    # see https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/SecgroupCommand.py
    # noinspection PyUnusedLocal
    @command
    def do_sec(self, args, arguments):
        """
        ::

            Usage:
                sec rule list [--cloud=CLOUDS] [--output=OUTPUT]
                sec rule add RULE FROMPORT TOPORT PROTOCOL CIDR
                sec rule delete RULE [--cloud=CLOUD]
                sec group list [--cloud=CLOUDS] [--output=OUTPUT]
                sec group add GROUP RULES DESCRIPTION
                sec group delete GROUP [--cloud=CLOUD]
                sec group load [GROUP] [--cloud=CLOUD]
                sec list [--output=OUTPUT]
                sec load
                sec clear

            Options:
                --output=OUTPUT Specify output format, in one of the following:
                                table, csv, json, yaml, dict
                                [default: table].
                --cloud=CLOUD   Name of the IaaS cloud e.g. kilo,chameleon.
                                The clouds are defined in the yaml file.
                                If the name "all" is used for the cloud all
                                clouds will be selected.
            Arguments:
                RULE          The security group rule name
                GROUP         The label/name of the security group
                FROMPORT      Staring port of the rule, e.g. 22
                TOPORT        Ending port of the rule, e.g. 22
                PROTOCOL      Protocol applied, e.g. TCP,UDP,ICMP
                CIDR          IP address range in CIDR format, e.g.,
                              129.79.0.0/16

            Examples:
                # sec load
                # sec group list
                # sec group add my_new_group webapp 8080 8080 tcp 0.0.0.0/0


            Bugs:
                # sec group list --cloud=chameleon
                # seg group delete my_group my_rule
                # sec group delete my_unused_group --cloud=kilo
                # sec group upload --cloud=kilo



            Description:


               Database commands:

                   sec clear
                       removes all rules and groups from the database

                   sec load
                        loads some default security groups and rules in the
                        database

                    sec clear
                        deletes all security groups and rules in the database

                    sec rule list  [--output=OUTPUT]
                        lists all security groups and rules in the database

                    sec rule add RULE FROMPORT TOPORT PROTOCOL CIDR
                        adds a security rule with the given group and the details
                        of the security rules

                    sec group add GROUP RULES DESCRIPTION
                        adds a security group with the given group and the
                        details of the security groups

                    sec rule delete RULE
                        deletes the rule form the database

                    sec group delete GROUP
                        deletes the group form the database


                Cloud commands:

                    sec rule list --cloud=CLOUDS [--output=OUTPUT]
                        lists all security rules in the specified cloud

                    sec group list --cloud=CLOUDS [--output=OUTPUT]
                        lists all security groups in the specified cloud

                    sec rule delete RULE --cloud=CLOUD
                        deletes the rule form the cloud

                    sec group delete GROUP [--cloud=CLOUD]
                        deletes the group from the cloud

                    sec load GROUP --cloud=CLOUD
                        uploads the group to the cloud with all its rules


        """

        no_cloud = "--cloud" not in arguments

        map_parameters(arguments,
                       'cloud',
                       'output',
                       'name')

        rules = SecgroupRule()
        groups = Secgroup()

        def Print(kind, liste):
            if kind == "group":
                output = ""
            else:
                output = groups.output

            print(Printer.write(liste,
                                sort_keys=output[kind]['sort_keys'],
                                order=output[kind]['order'],
                                header=output[kind]['header'],
                                output=arguments.output))

        def list_all():

            data = []

            group_entries = groups.list()

            for group_entry in group_entries:
                group_name = group_entry['name']

                for rule_name in group_entry['rules']:
                    try:
                        rule_entry = rules.list(name=rule_name)[0]
                        rule_entry['rule'] = rule_name
                        rule_entry['group'] = group_name
                        data.append(rule_entry)
                    except:
                        pass
            Print("all", data)

        if (arguments.load and not arguments.group) or \
            (arguments.load and arguments.group and not arguments.GROUP) \
            and no_cloud:

            examples = SecgroupExamples()
            examples.load()
            list_all()

            return ""

        elif arguments.load and arguments.group and arguments.cloud:

            provider = Provider(name=arguments.cloud)
            provider.upload_secgroup(name=arguments.GROUP)

            return ""

        elif arguments.list and not arguments.rule and not arguments.group:

            found = groups.list()
            for entry in found:
                group_rules = entry['rules']
                if type(group_rules) == list:
                    entry['rules'] = ', '.join(group_rules)

            Print("secgroup", found)

            found = rules.list()
            Print("secrule", found)

        elif arguments.group and arguments.delete:

            if arguments.cloud:
                clouds = Parameter.expand(arguments.cloud)
                for cloud in clouds:
                    print(f"cloud {cloud}")
                    provider = Provider(name=cloud)
                    r = provider.remove_secgroup(name=arguments.GROUP)

            else:
                groups.remove(arguments.GROUP)

        elif (arguments.group or arguments.rule) and arguments.list and \
            arguments.cloud:

            clouds = Parameter.expand(arguments.cloud)
            if len(clouds) == 0:
                variables = Variables()
                cloudname = variables['cloud']
                clouds = [cloudname]
            keys = []

            for cloud in clouds:
                print(f"cloud {cloud}")
                provider = Provider(name=cloud)
                cloud_groups = provider.list_secgroups()

                if arguments.output == 'table':
                    result = []
                    for group in cloud_groups:
                        if cloud == "aws":
                            for rule in group['IpPermissions']:
                                rule['name'] = group['GroupName']
                                rule['direction'] = "Inbound"
                                if rule['UserIdGroupPairs']:
                                    rule['groupId'] = \
                                        rule['UserIdGroupPairs'][0]['GroupId']
                                if rule['IpRanges']:
                                    rule['ipRange'] = rule['IpRanges'][0][
                                        'CidrIp']

                                result.append(rule)
                        else:
                            for rule in group['security_group_rules']:
                                rule['name'] = group['name']
                                result.append(rule)
                        cloud_groups = result
                provider.p.Print(cloud_groups,
                                 output=arguments.output,
                                 kind="secrule", )

            return ""

        elif arguments.group and arguments.list:
            found = groups.list()
            for entry in found:
                group_rules = entry['rules']
                if type(group_rules) == list:
                    entry['rules'] = ', '.join(group_rules)

            Print("secgroup", found)

            return ""

        elif arguments.rule and arguments.list:
            found = rules.list()
            Print("secrule", found)

            return ""

        elif arguments.rule and arguments.add:
            rules = SecgroupRule()
            #  name=None, protocol=None, ports=None, ip_range=None
            rules.add(
                name=arguments.RULE,
                ports=f"{arguments.FROMPORT}" + ":" + f"{arguments.TOPORT}",
                protocol=arguments.PROTOCOL,
                ip_range=arguments.CIDR
            )

            return ""

        elif arguments.group and arguments.add:
            group = Secgroup()
            group.add(
                name=arguments.GROUP,
                rules=arguments.RULES,
                description=arguments.DESCRIPTION
            )

            return ""

        elif arguments.list:

            found = rules.list()
            Print("secrule", found)

            return ""

        elif arguments.clear:

            groups.clear()
            rules.clear()

            return ""

        else:

            print("COMMNAD NOT FOUND")

        return ""
