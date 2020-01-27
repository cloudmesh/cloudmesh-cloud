# python cloudmesh/compute/awsboto/test_boto.py

import sys
import traceback
from pprint import pprint

import boto3
from cloudmesh.configuration.Config import Config

config = Config()
# pprint(config.data)
credentials = config['cloudmesh.cloud.awsboto.credentials']
pprint(credentials)
new_yaml_data_dict = {
    'User_5': {
        'Access Key Id': 2,
        'Secret Access Key Id': 'user2',
        'region name': 'us-west',
    }

}
# update_credential(new_yaml_data_dict,filepath)
'''
credentials:
        region: 'us-west-2'
        EC2_SECURITY_GROUP: 'group1'
        EC2_ACCESS_ID: TBD
        EC2_SECRET_KEY: TBD
        EC2_PRIVATE_KEY_FILE_PATH: '~/.cloudmesh/aws_cert.pem'
        EC2_PRIVATE_KEY_FILE_NAME: 'aws_cert'
'''
try:

    session = boto3.Session(
        aws_access_key_id=credentials['EC2_ACCESS_ID'],
        aws_secret_access_key=credentials['EC2_SECRET_KEY'],
        region_name=credentials['region'])
except:
    print("Access Key is not correct...Please try again..")
    sys.exit()
if session:
    pass

    # ec2_instance, ec2_ids = list_ec2_instance_id(session)
    # print(ec2_ids)

sys.exit()


# List all EC2 instance ID's in a particular region for a user

def list_ec2_instance_id(session):
    ec2_instance = session.resource('ec2')
    instance_ids = []
    for each_instance in ec2_instance.instances.all():
        instance_ids.append(each_instance.id)
    return ec2_instance, instance_ids


# Returns status of an EC2 instance

def get_ec2_instance_status(ec2_instance):
    state = []
    for each in ec2_instance.instances.all():
        print(each)
        state.append(each.id.state)
    return state

    return instance.state


# Starts an EC2 instance

def start_ec2_instance(session, instance_id):
    ec2 = session.client('ec2')
    print(instance_id)
    try:
        ec2.start_instances(InstanceIds=[instance_id])
        print("Instance starting..")
        ec2.wait_until_running()
        print("Instance started")
    except Exception as ex:
        traceback.print_exc()


# Stops an EC2 instance

def stop_ec2_instance(session, instance_id):
    ec2 = session.client('ec2')

    try:
        ec2.stop_instances(InstanceIds=[instance_id])
        print("Instance stopping..")

    except:
        print("EC2 Instance stopping failed...Try again..")

    # instance_state = get_ec2_instance_status(ec2_instance)
    print("currently instance state is {instance_state")

# start_ec2_instance(session,ec2_ids[0])
# stop_ec2_instance(session,ec2_ids[0])
