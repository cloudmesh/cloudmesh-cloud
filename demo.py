from deprecated.draft.vm.api.Vm import Vm


def main():
    test = Vm('aws')
    # test.start('i-0fad7e92ffea8b345')
    # test.stop('i-0fad7e92ffea8b345')
    print(test.list())
    # print(test.status('i-0fad7e92ffea8b345'))
    test.mongo.close_client()

    # test = Vm('azure')
    # print(test.list()[0].id)
    # test.start('i-0fad7e92ffea8b345')
    # test.stop('/subscriptions/97729f86-47bb-428b-98b6-835ef04c3553/resourceGroups/CLOUDMESH/providers/Microsoft.Compute/virtualMachines/cm-test-vm-1')
    # print(test.status('/subscriptions/97729f86-47bb-428b-98b6-835ef04c3553/resourceGroups/CLOUDMESH/providers/Microsoft.Compute/virtualMachines/cm-test-vm-1'))
    # test.mongo.close_client()

    # test = Vm('chameleon')
    # print(test.list()[0].id)
    # test.start('9bca2334-cac8-4cbd-bcdd-7af00f6345dc')
    # test.stop('9bca2334-cac8-4cbd-bcdd-7af00f6345dc')
    # print(test.status('9bca2334-cac8-4cbd-bcdd-7af00f6345dc'))
    # test.mongo.close_client()


if __name__ == "__main__":
    main()
