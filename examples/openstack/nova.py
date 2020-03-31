#!/usr/bin/env python

#
# pip install python-keystoneclient
# pip install python-novaclient
#

# python nova.py --os-auth-url=https://kvm.tacc.chameleoncloud.org:5000/v3 --os-user-domain-name=Default  --os-username=??? --os-password=??? 


import argparse
import pprint
import sys
import traceback

import keystoneauth1
from keystoneauth1 import loading
from keystoneclient.v3 import client as KeystoneClient
from novaclient import client as NovaClient

pp = pprint.PrettyPrinter(indent=4)


def main(argv):
    # Command line argument(s)
    parser = argparse.ArgumentParser(conflict_handler='resolve')
    loading.cli.register_argparse_arguments(parser, argv, default='password')
    args = parser.parse_args()

    # Open Keystone Authenticated Session
    auth = loading.load_auth_from_argparse_arguments(args)
    sess = keystoneauth1.session.Session(auth=auth)
    keystone = KeystoneClient.Client(session=sess)
    token = sess.get_token()
    domain_id = keystone.user_domain_id

    # Discover Compute Public Endpoint
    try:
        nova_url = sess.get_endpoint(service_type='compute', interface='public')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        exit(1)
    nova = NovaClient.Client(2.1, session=sess)

    # List Servers
    pp.pprint(nova.servers.list())


if __name__ == "__main__":
    main(sys.argv[1:])
