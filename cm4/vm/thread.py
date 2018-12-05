import threading
import time
import os


class Thread(threading.Thread):
    def __init__(self, vm, name, node_name, status):
        threading.Thread.__init__(self)
        self.vm = vm
        self.name = name
        self.node_name = node_name
        self.status = status

    def run(self):
        self.update_status()

    def update_status(self):
        count = 32
        print('Thread: updating the status of node')
        ping_check = False
        if self.status == 'running':
            ping_check = self.ping_public_ip()

        while self.vm.mongo.find_document('cloud', 'name', self.node_name)['state'] != self.status or ping_check:
            self.vm.info(self.node_name)
            if self.status == 'stopped':
                ping_check = False
            else:
                ping_check = self.ping_public_ip()
            time.sleep(count)
            if count < 2:
                print('Cannot get the newest status information')
                break
            count = count/2
        self.vm.info(self.node_name)

    def ping_public_ip(self):
        ip = self.vm.mongo.find_document('cloud', 'name', self.node_name)['public_ips']
        if len(ip) > 0:
            ping = os.system("ping -c 1 " + ip[0])
            return ping == 1
        else:
            return True
