# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 00:12:19 2018

@author: Rui
"""


from cm4.vm.Vm import Vm
from cm4.vm.VmRefactor import VmRefactor
from pprint import pprint

def main():

    # test for aws
    input("Press Enter to continue testing for AWS cloud....")
    provider = Vm('aws')
    refactor = VmRefactor(provider)




    # test for azure
    input("Press Enter to continue testing for Azure cloud....")
    provider = Vm('azure')



    # test for openstack
    input("Press Enter to continue testing for Chameleon cloud....")
    provider = Vm('chameleon')


    provider.mongo.close_client()

if __name__ == "__main__":
    main()