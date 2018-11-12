from cm4.flask_rest_api.app import app
from cm4.flask_rest_api.app import cloud
from flask import request, jsonify


@app.route('/')
@app.route('/index')
def index():
    return "This is the REST API for cm4"


@app.route('/vm/<vm_id>', methods=['GET'])
def get_vm_info(vm_id):
    """
    Returns the VM information for the provided vm_id.
    :param id: id of the VM
    :return: a json with the vm information
    """
    vm = cloud.find_one({'id' : vm_id})
    if not vm:
        return jsonify({'message': "The VM with the id: " + vm_id + " does not exist"}), 401

    del vm['_id']
    return jsonify({'VM': vm})
