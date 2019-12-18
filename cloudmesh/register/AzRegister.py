import random
import getpass
from time import sleep
from cloudmesh.common.console import Console
from sys import platform
import os

import subprocess
from cloudmesh.configuration.Config import Config

from pathlib import Path
import pandas
import re

# cloudmesh.cloud.azure.credentials.AZURE_TENANT_ID
# cloudmesh.cloud.azure.credentials.AZURE_SUBSCRIPTION_ID
# cloudmesh.cloud.azure.credentials.AZURE_APPLICATION_ID
# cloudmesh.cloud.azure.credentials.AZURE_SECRET_KEY


# PreRequisites: Install Azure CLI and follow Azure Account Creation Steps in Cloudmesh Manual

class AzRegister(object):

    def __init__(self, cloud='azure'):

        self.config = Config()
        self.credentials = self.config[f'cloudmesh.cloud.{cloud}.credentials']

    def set_credentials(self, creds):
        self.credentials['AZURE_TENANT_ID'] = creds['Access key ID']
        self.credentials['AZURE_SUBSCRIPTION_ID'] = creds['Secret access key']
        self.credentials['AZURE_APPLICATION_ID'] = creds['Secret access key']
        self.credentials['AZURE_SECRET_KEY'] = creds['Secret access key']
        self.config.save()

    def azString2Dict(self, azString):
        azDict = dict()
        for i in azString.strip().splitlines():
            x = i.split(":")
            if len(x) == 2:
                azDict[x[0].strip(' ,"')] = x[1].strip(' ,"')
        return azDict

    def register(self, cloud='azure'):
        # Opens web browser and prompts user to login
        subprocess.Popen('az login')

        # once user has logged in, collects account information, such as subscription id
        accountInfo = subprocess.getoutput('az account show')
        print(accountInfo)

        azoutput = self.azString2Dict(accountInfo)

        AZURE_SUBSCRIPTION_ID = azoutput['id']
        AZURE_TENANT_ID = azoutput['tenantId']

        # WARNING: FOLLOWING CODE WILL RENDER OLD SECRET KEY INVALID
        azAppKeyStr = subprocess.getoutput('az ad sp create-for-rbac --name http://cloudmesh')
        azAppKeyDict = self.azString2Dict(azAppKeyStr)

        AZURE_APPLICATION_ID = azAppKeyDict['appId']
        AZURE_SECRET_KEY = azAppKeyDict['password']

        creds = {
            'AZURE_SUBSCRIPTION_ID': AZURE_SUBSCRIPTION_ID,
            'AZURE_TENANT_ID': AZURE_TENANT_ID,
            'AZURE_APPLICATION_ID': AZURE_APPLICATION_ID,
            'AZURE_SECRET_KEY': AZURE_SECRET_KEY
        }

        self.set_credentials(creds)

        Console.info(
            "Azure Tenant, Subscription, Application, and Secret Key have been added to the cloudmesh.yaml file.")
