from deprecated.draft.openstack import OpenstackCM
from time import sleep
import datetime


# testcode
# need extra waiting time so server can finish update the node status
# pending - running - stopped

def main():
    d = OpenstackCM('chameleon')

    # create and auto start
    print("call d.create() function")
    node = d.create('cm_test_small')
    node_id = node.id
    # node_id = "826d57a4-8810-412f-9be8-b738b9facb58"
    # print(node)

    # print(d.info(node_id))
    # print(d.node_info(node_id))

    print("Node:" + node_id + " has been set up")

    while d.info(node_id)['state'] == 'pending':
        sleep(3)
    print("At time " + str(datetime.datetime.now()) + " the state is " + d.info(node_id)['state'])

    # suspend
    print("call d.suspend() function")
    d.suspend(node_id)
    while d.info(node_id)['state'] == 'running':
        sleep(3)
    print("At time " + str(datetime.datetime.now()) + " the state is " + d.info(node_id)['state'])

    # resume
    print("call d.resume() function")
    d.resume(node_id)
    while d.info(node_id)['state'] == 'stopped':
        sleep(3)
    print("At time " + str(datetime.datetime.now()) + " the state is " + d.info(node_id)['state'])

    # stop
    print("call d.stop() function")
    d.stop(node_id)
    while d.info(node_id)['state'] == 'running':
        sleep(3)
    print("At time " + str(datetime.datetime.now()) + " the state is " + d.info(node_id)['state'])

    # restart
    print("call d.restart() function")
    d.start(node_id)
    sleep(10)
    print("At time " + str(datetime.datetime.now()) + " the state is " + d.info(node_id)['state'])

    # destroy
    print("call d.destroy() function")
    d.destroy(node_id)
    sleep(10)


if __name__ == "__main__":
    main()
