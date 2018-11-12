## CM4 REST Api

The cm4 REST Api is built using flask and provides the cloud information retrieval functionality through HTTP calls.

#### Pre-requisites
Use pip install to install the following packages.

Flask
Flask-PyMongo

#### Examples
- Retrieve information about a VM \
  ```bash 
  curl localhost:5000/vms/i-0fad7e92ffea8b345
  ```