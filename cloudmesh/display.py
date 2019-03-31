class Display(dict):

    def __init__(self):
        self = {}

    def openstack(self):
        data = {
        "vm": {
            "sort_keys": ["name"],
            "order": ["name",
                      "cloud",
                      "state",
                      "image",
                      "public_ips",
                      "private_ips",
                      "kind"],
            "header": ["name",
                       "cloud",
                       "state",
                       "image",
                       "public_ips",
                       "private_ips",
                       "kind"]
        },
        "image": {"sort_keys": ["name",
                                "extra.minDisk"],
                  "order": ["name",
                            "extra.minDisk",
                            "updated",
                            "driver"],
                  "header": ["Name",
                             "MinDisk",
                             "Updated",
                             "Driver"]},
        "flavor": {"sort_keys": ["name",
                                 "vcpus",
                                 "disk"],
                   "order": ["name",
                             "vcpus",
                             "ram",
                             "disk"],
                   "header": ["Name",
                              "VCPUS",
                              "RAM",
                              "Disk"]}
        }