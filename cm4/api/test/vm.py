import random
from flask import jsonify


STATUSES = ["running", "stopped", "paused"]
REGIONS = ["usnorthcentral", "useast", "uswest", "ussouth"]
PROVIDERS = ["aws", "azure", "openstack"]
FLAVORS = []
SIZES = []


def vm_list():
    vms = []
    vms.append(_get_test_vm(1))
    return jsonify(vms)


def _get_test_vm(num):
    vm = dict(
        id=f'ID-{num}',
        provider=f'Provider{num}',
        name=f'Name-{num}',
        image=f'Image-{num}',
        region=f'Region-{num}',
        size=f'Size-{num}',
        state=f'State-{num}',
        private_ips=f'PrivateIPs-{num}',
        public_ips=f'PublicIPs-{num}',
        metadata=f'Meta-{num}',
    )

    return vm
