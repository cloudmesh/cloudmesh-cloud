####################################################################################
#            A W S    E C 2  I N S T A N C E  A U T O M A T I O N                  #
#                                                                                  #
#     AUTHOR: SAURABH SWAROOP                                                      #
#             INDIANA UNIVERSITY                                                   #
####################################################################################                                   
import boto3
import yaml
import os
import traceback
import sys


############### Loads Credentials Yaml file and returns all aws users

def yaml_loader(filepath):
	with open(filepath,"r") as file_descriptor:
		data = yaml.safe_load(file_descriptor)
	return data

############## Adds new user to Credentials Yaml file

def update_credential(new_data,filepath):


	with open(filepath,'r') as yamlfile:
		credentials = yaml.safe_load(yamlfile)
		credentials.update(new_data)
	if credentials:
		with open(filepath,'w') as updatedfile:
			yaml.safe_dump(credentials,updatedfile,default_flow_style = False)

# List all EC2 instance ID's in a particular region for a user

def list_ec2_instance_id(session):
	ec2_instance = session.resource('ec2')
	instance_ids = []
	for each_instance in ec2_instance.instances.all():
		instance_ids.append(each_instance.id)
	return ec2_instance,instance_ids

########## Returns status of an EC2 instance

def get_ec2_instance_status(ec2_instance):
	state = []
	for each in ec2_instance.instances.all():
		print(each)
		state.append(each.id.state)
	return state

	
	return instance.state

########## Starts an EC2 instance

def start_ec2_instance(session,instance_id):

	ec2 = session.client('ec2')
	print(instance_id)
	try:
		ec2.start_instances(InstanceIds=[instance_id])
		print("Instance starting..")
		ec2.wait_until_running()
		print("Intance started")
	except Exception as ex:
		traceback.print_exc()
		
########## Stops an EC2 instance       

def stop_ec2_instance(session,instance_id):

	ec2 = session.client('ec2')
	
	try:
		ec2.stop_instances(InstanceIds=[instance_id])
		print("Instance stopping..")
		
	except:
		print("EC2 Instance stopping failed...Try again..")
        


if __name__ == "__main__":

	filepath = "credentials.yaml"
	data = yaml_loader(filepath)
	
	for key, value in data.items() :
		if value is not None:
			print(value['Access Key Id'])
			print(value['Secret Access Key Id'])

	new_yaml_data_dict = {
		'User_5':{
			'Access Key Id': 2, 
            'Secret Access Key Id': 'user2', 
            'region name': 'us-west', 
		}

	}
	# update_credential(new_yaml_data_dict,filepath)


	try:
		
		session = boto3.Session(aws_access_key_id=data['User_1']['Access Key Id'],
                                         aws_secret_access_key=data['User_1']['Secret Access Key Id'],region_name = data['User_1']['region name'])
	except:
		print("Access Key is not correct...Please try again..")
		sys.exit()
	if session:
		ec2_instance,ec2_ids = list_ec2_instance_id(session)
	print(ec2_ids)

	instance_state = get_ec2_instance_status(ec2_instance)
	print("currently instance state is {instance_state")

	#start_ec2_instance(session,ec2_ids[0])
	#stop_ec2_instance(session,ec2_ids[0])

