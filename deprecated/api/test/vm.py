import random
from random import randint
from flask import jsonify

VMS = {}    # TODO: keep vm list in memory
STATUSES = ["running", "stopped", "paused"]
REGIONS = ["usnorthcentral", "useast", "uswest", "ussouth", "us-west-2", "us-west-1", "us-east-1"]
PROVIDERS = ["aws", "azure", "chameleon"]
IMAGES = ["Canonical:UbuntuServer:16.04-LTS:latest", "ami-0bbe6b35405ecebdb", "CC-Ubuntu16.04"]
SIZES = ["t2.micro", "Basic_A0", "m1.small"]


def vm_list(how_many=100):
    vms = []
    for i in range(1, how_many + 1):
        vms.append(_random_vm(i))
    return jsonify(vms)


def _random_vm(num):
    return dict(
        id=f'ID-{num}',
        provider=random.choice(PROVIDERS),
        name=f'Name-{num}',
        image=random.choice(IMAGES),
        region=random.choice(REGIONS),
        size=random.choice(SIZES),
        state=random.choice(STATUSES),
        private_ips=f"{_random_ip()},{_random_ip()}",
        public_ips=f"{_random_ip(), _random_ip()}",
        metadata=f'Metadata-{num}',
    )


def _random_ip():
    return f"{randint(0, 255)}.{randint(0, 255)}.{randint(0, 255)}.{randint(0, 255)}"
