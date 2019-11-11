from cloudmesh.compute.azure import Provider as prv
from cloudmesh.compute.vm import Provider as parentPrv
from azure.cli.core import get_default_cli
import time
import json

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


account = {}
sp_cred = {}
# try:
#     account.update(get_az_account_list())
#
#     sp_cred.update(get_service_principal_credentials())
#     time.sleep(2)
#
#     # sleep for couple of seconds because it takes sometime
#     # to update the credentials
# except ValueError:
#     az_login()
#     account = get_az_account_list()

# print(account)
# print(sp_cred)
#
# cred = {
#     'AZURE_APPLICATION_ID': sp_cred['appId'],
#     'AZURE_SECRET_KEY': sp_cred['password'],
#     'AZURE_TENANT_ID': account['tenantId'],
#     'AZURE_SUBSCRIPTION_ID': account['id'],
# }
# print("Cred: " + str(cred))

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
print(p.create(secgroup='test'))

print('$$$$$$$$$$$$$$$$$$$$ create second vm')
print(p.create(secgroup='test'))

# print('$$$$$$$$$$$$$$$$$$$$ destroy')
# print(p.destroy())

pass
