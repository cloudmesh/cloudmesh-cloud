from azure.cli.core import get_default_cli
from cloudmesh.compute.vm import Provider as parentPrv

# AZURE_CLI = 'az'
SERVICE_PRINCIPAL = 'cloudmesh'

cli = get_default_cli()


def get_az_account_list():
    cli.invoke(['account', 'list'])
    res = cli.result
    return res.result[0]


def az_login():
    cli.invoke(['login'])


def get_service_principal_credentials():
    cli.invoke(['ad', 'sp', 'create-for-rbac', '--name', SERVICE_PRINCIPAL])
    res = cli.result
    return res.result


p = parentPrv.Provider('azure')

print('$$$$$$$$$$$$$$$$$$$$ secgroup')
print(p.add_secgroup('test'))
p.list_secgroups()

print('$$$$$$$$$$$$$$$$$$$$ rules')
print(p.add_secgroup_rule(name='ssh-test'))
p.list_secgroups_rules()

print('$$$$$$$$$$$$$$$$$$$$ rule to group and upload')
print(p.add_rules_to_secgroup(name='test', rules=['ssh-test', 'ssh']))
print(p.upload_secgroup('test'))

print('$$$$$$$$$$$$$$$$$$$$ create vm')
print(p.create(name='vm1'))

print('$$$$$$$$$$$$$$$$$$$$ create vm')
print(p.list())

print('$$$$$$$$$$$$$$$$$$$$ create second vm')
print(p.create(name='vm2', secgroup='test'))

print('$$$$$$$$$$$$$$$$$$$$ ssh vm')
p.ssh('vm1', '\"echo xxxx\"')

print('$$$$$$$$$$$$$$$$$$$$ destroy')
print(p.destroy())

pass
