from cm4.vm.Vm import Vm

def main():
    test = Vm('aws')
    #test.start('i-0fad7e92ffea8b345')
    #test.stop('i-0fad7e92ffea8b345')
    print(test.status('i-0fad7e92ffea8b345'))
    test.mongo.close_client()


if __name__ == "__main__":
    main()