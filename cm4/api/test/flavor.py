import random
import uuid
from flask import jsonify
from random import randint
from cm4.api.test.vm import SIZES, PROVIDERS

RAMS = [4294967296, 8589934592, 12884901888, 17179869184, 34359738368]
DISKS = [10737418240, 21474836480, 32212254720, 53687091200, 1099511627776]


def get_flavor():
    return jsonify(_random_flav("default"))


def add_flavor(flavor):
    return flavor


def get_flavor_by_name(name):
    random_flav = _random_flav(name)
    random_flav["name"] = name
    return random_flav


def _random_flav(name):
    return dict(
        name=random.choice(SIZES),
        id=f"ID-{name}",
        label=f"Label-{name}",
        metadata=f"Metadata-{name}",
        uuid=f"{uuid.uuid4()}",
        ram=random.choice(RAMS),
        disk=random.choice(DISKS),
        price=f"${randint(0,2)}.{0,9}{0,9}/hr",
        cloud=random.choice(PROVIDERS),
        cloud_id=f"CloudID-{name}"
    )
