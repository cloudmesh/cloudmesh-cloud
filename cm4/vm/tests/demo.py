from cm4.vm.Vm import Vm
from pprint import pprint
from cm4.configuration.name import Name
import sys

def main():

    provider = Vm('aws')
    #print(provider.get_public_ips('a-b=luoyu-0'))
    #print(provider.list())
    #pprint(provider.start('a-b=luoyu-0'))
    #pprint(provider.stop('a-b=luoyu-0'))
    #print(provider.status('a-b=luoyu-0'))
    #pprint(vars(provider.info('a-b=luoyu-0')))
    #pprint(vars(provider.create ('a-b=luoyu-1')))
    #pprint(provider.destroy ('a-b=luoyu-1'))
    #provider.size_image()

    #provider = Vm('azure')
    #print(provider.list())
    #pprit(provider.start('cm-test-vm-1'))
    #pprint(provider.stop('cm-test-vm-1'))
    #print(provider.status('cm-test-vm-1'))
    #pprint(vars(provider.info('cm-test-vm-1')))


    #provider = Vm('chameleon')
    #print(provider.list())
    #pprit(provider.start('cm_test'))
    #pprint(provider.stop('cm_test'))
    #print(provider.status('cm_test'))
    #pprint(vars(provider.info('cm_test')))

    provider.mongo.close_client()

if __name__ == "__main__":
    main()