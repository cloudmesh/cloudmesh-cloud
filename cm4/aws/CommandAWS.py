from cm4.configuration.config import Config
from cm4.cmmongo.mongoDB import MongoDB
import subprocess


class CommandAWS(object):

    def __init__(self):
        config = Config()
        self.private_key_file = config.get('cloud.aws.credentials.EC2_PRIVATE_KEY_FILE_PATH')
        self.mongo = MongoDB(host=config.get('data.mongo.MONGO_HOST'),
                             username=config.get('data.mongo.MONGO_USERNAME'),
                             password=config.get('data.mongo.MONGO_PASSWORD'),
                             port=config.get('data.mongo.MONGO_PORT'))

    def find_node_dns(self, vm_name):
        """
        based on AWS design, we need to get the DNS of the required nodes
        :param vm_name: the name of vm
        :return: the DNS
        """

        dns = self.mongo.find_document('cloud', 'name', vm_name).get('extra').get('dns_name')
        return dns

    def read_script(self, script):
        """
        read the script file

        :param script: the script that would be run in instance
        :return content: the content of the script
        """

        content = open(script, "r").read()
        return content

    def run_command(self, command, vm_name):
        """
        run command in the vm, and save the job information into MongoDB
        :param command: the command string
        :param vm_name: the vm name
        :return: the result of command
        """
        username = 'ubuntu@'+self.find_node_dns(vm_name)
        job_id = self.job_start_update_mongo('Null', command, vm_name)
        self.update_instance_job_status(vm_name, job_id)
        temp = subprocess.check_output(['ssh', '-i', self.private_key_file, username, command]).decode("utf-8")
        self.job_end_update_mongo(job_id, temp)
        self.update_instance_job_status(vm_name, job_id)

        return 'Running command ' + command + 'in Instance ' + vm_name + ':\n' + temp

    def run_script(self, script, vm_name):
        """
        run script in the vm, and save the job information into MongoDB
        :param script: the raw shell script file
        :param vm_name: the vm name
        :return: the result of script
        """
        username = 'ubuntu@' + self.find_node_dns(vm_name)
        content = self.read_script(script)

        job_id = self.job_start_update_mongo(content, 'Null', vm_name)
        self.update_instance_job_status(vm_name, job_id)
        temp = subprocess.check_output(['ssh', '-i', self.private_key_file, username, content]).decode("utf-8")
        self.job_end_update_mongo(job_id, temp)
        self.update_instance_job_status(vm_name, job_id)

        return 'Running command ' + script + 'in Instance ' + vm_name + ':\n' + temp


    def job_start_update_mongo(self, script, command, vm_name):
        """
        create new job document in MongoDB, status is processing
        :param script: the running script
        :param command: the input command
        :param vm_name: the vm name
        :return: the job document id
        """
        job = self.mongo.job_document(vm_name, 'processing', script, 'Null', 'Null', command)
        return self.mongo.insert_job_collection(job)


    def job_end_update_mongo(self, document_id, output):
        """
        jod is done, update the information into job collection in MongoDB, status is done
        :param document_id: the job document id
        :param output: the result
        :return: True/False
        """
        return self.mongo.update_document('job', '_id', document_id, dict(status='done', output=output))


    def update_instance_job_status(self, vm_name, job_id):
        """
        for each node, it has its own status. when job is running, it will update its currentJob. When the jon id one,
        currentJob is Null, and history will be update
        :param vm_name: the name of vm
        :param job_id: jod id
        """
        status = self.mongo.find_document('status', 'name', vm_name)
        if status:
            self.mongo.insert_status_collection(self.mongo.status_document(vm_name, 'processing', job_id, []))
        else:
            history = status['history']
            if status['currentJob'] == job_id:
                history.append(job_id)
                self.mongo.update_document('status', 'id', vm_name, dict(status='No Job', currentJob='Null',
                                                                         history=history))
            else:
                self.mongo.update_document('status', 'id', vm_name, dict(status='processing', currentJob=job_id))


    def disconnect(self):
        """
        disconnect from mongodb
        """
        self.mongo.close_client()
