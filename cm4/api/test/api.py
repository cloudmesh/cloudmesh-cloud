import connexion
from pathlib import Path
from os import path
from specsynthase.specbuilder import SpecBuilder


if __name__ == "__main__":
    spec_dir = "../specs"

    # Currently does not work because each yaml file is technically defining
    # its own *separate* swagger api.
    # Error: swagger key already exists
    #
    # current_dir = path.dirname(__file__)
    # spec_path = Path(f"{current_dir}/{spec_dir}").resolve()
    #
    # spec = SpecBuilder()\
    #     .add_spec(spec_path.joinpath("vm/vm.yaml")) \
    #     .add_spec(spec_path.joinpath("flavor/flavor.yaml"))

    spec = "vm/vm.yaml"

    app = connexion.App(__name__, specification_dir=spec_dir)
    app.add_api(spec)
    app.run(port=8080, debug=True)
