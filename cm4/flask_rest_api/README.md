## CM4 REST Api

The cm4 REST Api is built using flask and provides the cloud information retrieval functionality through HTTP calls.

#### Pre-requisites

Use pip install to install the following packages.

- Flask
- Flask-PyMongo

#### How to run the REST API

- Navigate to the cm directory. example:
```bash
cd ~/git/cloudmesh/cm
```

- Add the cm directory to the Python Path
```bash
export PYTHONPATH=$PYTHONPATH:$PWD
```

- Run the REST API
```bash
python cm4/flask_rest_api/rest_api.py
```

#### API

- /vms/ : Provides information on all the VMs.
- /vms/stopped  : Provides information on all the stopped VMs.
- /vms/<id> : Provides information on the VM identified by the <id>


#### Examples

- Retrieve information about a VM
  ```bash 
  curl localhost:5000/vms/i-0fad7e92ffea8b345
  ```

