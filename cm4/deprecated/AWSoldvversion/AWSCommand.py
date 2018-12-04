from cm4.abstractclass.ProcessManagerABC import ProcessManagerABC
from cm4.deprecated.AWSoldvversion.AWSController import AWSController
from cm4.cmmongo.mongoDB import MongoDB
import subprocess


class AWSCommand(ProcessManagerABC):

    def __init__(self, **kwargs):
        """
        initialize the mongodb connection, ger required information to access nodes in AWS
        :param kwargs: port, username, password for mongodb
        """
        self.database = MongoDB()
        self.database.set_port(kwargs['port'])
        self.database.set_username(kwargs['username'])
        self.database.set_password(kwargs['password'])
        self.database.connect_db()
        credential = self.database.find_document('cloud', 'kind', 'aws')
        self.controller = AWSController(credential['EC2_ACCESS_ID'],
                                        credential['EC2_SECRET_KEY'], credential['EC2_REGION'])
        self.ssh_key = credential['EC2_PRIVATE_KEY_FILE']

    def check_running_node(self, list_id):
        """
        user inputs list of node ids, check the node is running or not
        :param list_id: list of required node id
        :return: stopped node id
        """
        list_instance_status = self.controller.ls()
        stopped_instance = []
        for i in list_id:
            for id, name, state in list_instance_status:
                if i == id and state != 'running':
                    stopped_instance.append([i, state])
        return stopped_instance

    def find_node_DNS(self, name_id):
        """
        based on AWS design, we need to get the DNS of the required nodes
        :param name_id: node is
        :return: the DNS
        """
        nodes = self.controller.ls()
        required_id = ''
        for i in nodes:
            if i.name == name_id or i.id == name_id:
                required_id = i.id
        DNS = self.controller.info(required_id)['extra']['dns_name']
        return DNS

    def read_script(self, script):
        """
        read the script file

        :param script: the script that would be run in instance
        :return content: the content of the script
        """
        content = open(script, "r").read()
        return content

    def run_command(self, command, vm_list):
        """
        running command in nodes, update the job and status document in MongoDB
        :param command: the input command
        :param vm_list: list of node id
        :return: the result of each node
        """
        output = []
        for i in vm_list:
            username = 'ubuntu@'+self.find_node_DNS(i)
            job_id = self.start_job('Null', command, i)
            self.update_status(i, job_id)
            temp = subprocess.check_output(['ssh', '-i', self.ssh_key, username,
                                            command]).decode("utf-8")
            self.end_job(i, temp)
            self.update_status(i, job_id)
            output.append('Running command: ' + command + ' in Instance(name or id) ' + i + ':\n' + temp)
        return output

    def run_script(self, script, vm_list):
        """
        running script in nodes, update the job and status document in MongoDB
        :param script: the input script
        :param vm_list: list of node id
        :return: the result of each node
        """
        content = self.read_script(script)
        output = []
        for i in vm_list:
            username = 'ubuntu@' + self.find_node_DNS(i)
            job_id = self.start_job(content, 'Null', i)
            self.update_status(i, job_id)
            temp = subprocess.check_output(['ssh', '-i', self.ssh_key, username, content]).decode ("utf-8")
            self.end_job(i, temp)
            self.update_status(i, job_id)
            output.append('Running command: ' + script + ' in Instance(name or id) ' + i + ':\n' + temp)
        return output

    def parallel(self):
        print('working on it')

    def start_job(self, script, command, vm):
        """
        create new job document in MongoDB, status is processing
        :param script: the running script
        :param command: the input command
        :param vm: the node id
        :return: the job document id
        """
        job = self.database.job_document(vm, 'processing', script, 'Null', 'Null', command)
        return self.database.insert_job_collection(job)

    def end_job(self, ID, output):
        """
        jod is done, update the information into job collection in MongoDB, status is done
        :param ID: the job document id
        :param output: the result
        :return: True/False
        """
        return self.database.update_document('job', ID, dict(status='done', output=output))

    def update_status(self, vm, job_id):
        """
        for each node, it has its own status. when job is running, it will update its currentJob. When the jon id one,
        currentJob is Null, and history will be update
        :param vm: node id
        :param job_id: jod id
        """
        status = self.database.find_document('status', '_id', vm)
        history = status['history']
        if status['currentJob'] == job_id:
            self.database.update_document('status', vm, dict(currentJob='Null', history=history.append(job_id)))
        else:
            self.database.update_document('status', vm, dict(currentJob=job_id))

    def disconnect(self):
        """
        disconnect from mongodb
        """
        self.database.close_client()

