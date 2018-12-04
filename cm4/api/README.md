Open API 2.0 Rest
===


The API endpoints are defined as [OpenAPI 2.0](https://swagger.io/docs/specification/2-0/basic-structure/) specs
located in the [nist](https://github.com/cloudmesh-community/nist) repository.


### Getting Started

**Download Specs**

From the repository root, run:

```bash
$ make nist-install
```

This will download the nist repository as a sibling to the current `cm` repository and then copy
the specs into the `api/specs` folder. These specs will be referenced by 
[connexion](https://connexion.readthedocs.io/en/latest/) to generate the request handlers and match them to resolvers.

*Note:* After this initial install, `make nist-copy` can be used to copy over local changes from `../nist/`.

**Install requirements**

Currently the requirements for running the api are not included in the project's base requirements.
Ensure that both `flask` and `connexion` are pip installed.

```bash
pip install -r cm4/api/requirements.txt
```

**Run the API**

```bash
python cm4/api/api.py
```

or

```bash
python cm4/api/test/api.py
```

The UI is served at [http://localhost:8080/cloudmesh/v3/ui/](http://localhost:8080/cloudmesh/v3/ui/)

