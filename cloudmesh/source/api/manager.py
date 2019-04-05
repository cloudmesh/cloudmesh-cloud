import os
from pprint import pprint
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.util import path_expand
from cloudmesh.common.console import Console
from cloudmesh.management.script import Script

class Manager(object):

    def __init__(self, config, protocol="ssh"):

        self.config = config
        self.data = {}

        for software in config:

            self.data[software] = source = dotdict(
                {
                    "software": software,
                    "directory": path_expand(config[software]),

                }
            )
            if software in ["cm"]:
                source["community"] = "cloudmesh-community"
                source["preface"] = ""
            else:
                source["community"] = "cloudmesh"
                source["preface"] = "cloudmesh."

            source["path"] = os.path.join(config[software],
                                          source["preface"] + software)

            if format == "ssh":
                source[
                    "git"] = "git@github.com:{community}/{preface}{software}.git".format(
                    **dict(source))
            else:
                source[
                    "git"] = "https://github.com/{community}/{preface}{software}.git".format(
                    **dict(source))


    def clean(self):
        script = f"""
                    rm -rf *.zip
                    rm -rf *.egg-info
                    rm -rf *.eggs
                    rm -rf docs/build
                    rm -rf build
                    rm -rf dist
                    find . -name '__pycache__' -delete
                    find . -name '*.pyc' -delete
                    rm -rf .tox
                    rm -f *.whl
                """

        installer = Script.run(script)
        print(installer)

    def patch(self, package):
        script = f"""
                    bump2version --allow-dirty patch
	                python setup.py sdist bdist_wheel
                    twine check dist/*
	                twine upload --repository testpypi  dist/*
                    sleep 10    
	                pip install --index-url https://test.pypi.org/simple/ cloudmesh-{package} -U
                  """
        installer = Script.live(script)
        #print (installer)

    def dist(self):
        script = f"""
                    python setup.py sdist bdist_wheel
	                twine check dist/*
                  """
        installer = Script.live(script)
        #print (installer)

    def minor(self):
        script = f"bump2version minor --allow-dirty"
        installer = Script.live(script)
        # print (installer)


    def release(self):
        with open("VERSION") as f:
            version=f.read().strip()
        script = f''''
                    git tag "v{version}"
                    git push origin master --tags
                    python setup.py sdist bdist_wheel
                    twine check dist/*
                    twine upload --repository pypi dist/*
                    sleep 10
                    pip install -U cloudmesh-common
                '''
        installer = Script.live(script)
        #print (installer)


    def install(self):

        for software in self.config:
            source = self.data[software]
            if not os.path.exists(source["path"]):
                source["command"] = "cd {path}; git pull".format(**dict(source))
            else:
                source[
                    "command"] = "cd {directory}; git clone {software}".format(
                    **dict(source))

        pprint(self.data)
        for software in self.config:
            command = path_expand(self.data[software]['command'])
            Console.ok(command)
            os.system(command)

    def update(self):
        print("update", self.config)

    def dict(self):
        return self.data
