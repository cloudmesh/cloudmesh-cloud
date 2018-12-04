from cm4.vm.Vm import Vm
from pprint import pprint
from cm4.configuration.name import Name
import sys


def main():
    provider = Vm('aws')

    # print(provider.list())
    # pprit(provider.start('a-b=luoyu-0'))
    # provider.stop('a-b=luoyu-0')
    # pprint(provider.stop('a-b=luoyu-0'))
    # print(provider.status('a-b=luoyu-0'))
    # pprint(vars(provider.info('a-b=luoyu-0')))

    provider = Vm('azure')
    # print(provider.list())
    # pprit(provider.start('a-b=luoyu-1'))
    # provider.stop('a-b=luoyu-1')
    # pprint(provider.stop('a-b=luoyu-1'))
    # print(provider.status('a-b=luoyu-1'))
    # pprint(vars(provider.info('a-b=luoyu-1')))

    provider = Vm('chameleon')
    # print(provider.list())
    # pprit(provider.start('a-b=luoyu-2'))
    # provider.stop('a-b=luoyu-2')
    # pprint(provider.stop('a-b=luoyu-2'))
    # print(provider.status('a-b=luoyu-2'))
    # pprint(vars(provider.info('a-b=luoyu-2')))

    provider.mongo.close_client()


if __name__ == "__main__":
    main()
