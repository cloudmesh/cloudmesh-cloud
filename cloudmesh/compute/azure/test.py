from cloudmesh.compute.azure import Provider as prv
from cloudmesh.common.Shell import Shell

import json

AZURE_CLI = 'az'
SERVICE_PRINCIPAL = 'http://cloudmeshtest'


def get_az_account_list():
    s = Shell.execute(AZURE_CLI, ['account', 'list'])
    return json.loads(s[s.find('[') + 1: s.find(']')])


def az_login():
    Shell.execute('az', ['login'])


def get_service_principal_credentials():
    s = Shell.execute(AZURE_CLI,
                      ['ad', 'sp', 'create-for-rbac', '--name',
                       SERVICE_PRINCIPAL])
    return json.loads(s[s.find('{'): s.find('}') + 1])


account = {}
sp_cred = {}
try:
    account.update(get_az_account_list())
    sp_cred.update(get_service_principal_credentials())
except ValueError:
    az_login()
    account = get_az_account_list()

print(account)
print(sp_cred)

cred = {
    'AZURE_APPLICATION_ID': sp_cred['appId'],
    'AZURE_SECRET_KEY': sp_cred['password'],
    'AZURE_TENANT_ID': account['tenantId'],
    'AZURE_SUBSCRIPTION_ID': account['id'],
}

p = prv.Provider(credentials=cred)

p.list()

pass
