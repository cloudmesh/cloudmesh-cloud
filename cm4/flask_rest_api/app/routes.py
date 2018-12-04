from cm4.flask_rest_api.app import app
from cm4.flask_rest_api.app import cloud
from flask import request, jsonify


@app.route('/')
@app.route('/index')
def index():
    return "This is the REST API for cm4"


@app.route('/vms/', methods=['GET'])
def get_all_vms():
    """
    Returns all the VM information.
    :return: a json with all the vm information
    """
    vms = cloud.find()
    if not vms:
        return jsonify({'message': "There are no VMs in the system"}), 401

    vm_dict = {}
    for vm in vms:
        del vm['_id']
        vm_dict[vm["id"]] = vm

    return jsonify({'VMs': vm_dict})


@app.route('/vms/stopped/', methods=['GET'])
def get_stopped_vms():
    """
    Returns all the stopped VM information.
    :return: a json with all the stopped vm information
    """
    vms = cloud.find({'state': 'stopped'})
    if not vms:
        return jsonify({'message': "There are no stopped VMs in the system"}), 401

    vm_dict = {}
    for vm in vms:
        del vm['_id']
        vm_dict[vm["id"]] = vm

    return jsonify({'StoppedVMs': vm_dict})


@app.route('/vms/<vm_id>', methods=['GET'])
def get_vm_info(vm_id):
    """
    Returns the VM information for the provided vm_id.
    :param vm_id: id of the VM
    :return: a json with the vm information
    """
    vm = cloud.find_one({'id': vm_id})
    if not vm:
        return jsonify({'message': "The VM with the id: " + vm_id + " does not exist"}), 401

    del vm['_id']
    return jsonify({'VM': vm})
