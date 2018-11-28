import connexion


if __name__ == "__main__":
    app = connexion.App(__name__, specification_dir="../specs")
    app.add_api("vm/vm.yaml")
    app.run(port=8080, debug=True)
