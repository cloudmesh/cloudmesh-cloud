"""
Main module of the server file
"""

# see the example in https://github.com/cloudmesh-community/nist/tree/master/examples/flask-connexion-swagger

import connexion
from flask import jsonify

# Create the application instance

# TODO:
#
location = "~/.cloudmesh/openai this is still needs to be expanded"
app = connexion.App(__name__, specification_dir=location)

# Read the yaml file to configure the endpoints

# app.add_api("queue.yaml")
app.add_api("batch.yaml")


# create a URL route in our application for "/"
@app.route("/")
def home():
    msg = {"msg": "It's working!"}
    return jsonify(msg)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
