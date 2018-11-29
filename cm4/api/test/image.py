import random
from flask import jsonify
from random import randint
from cm4.api.test.vm import PROVIDERS, IMAGES

TAGS = ["web server", "db", "compute", "proxy"]
OS = ["linux", "windows", "darwin"]


def get_image():
    return jsonify(_random_image("default"))


def get_image_by_name(name):
    random_image = _random_image(name)
    random_image["name"] = name
    return jsonify(random_image)


def add_image(image):
    return jsonify(image)


def _random_image(name):
    return dict(
        id=f"ID-{name}",
        name=random.choice(IMAGES),
        tag=random.choice(TAGS),
        description=f"Description-{name}",
        cloud=random.choice(PROVIDERS),
        os=random.choice(OS),
        osVersion=f"{randint(0,5)}.{randint(0,11)}",
        status=f"Status-{name}",
        visibility=f"Visibility-{name}",
        extra=f"Extra-{name}"
    )
