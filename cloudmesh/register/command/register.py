from pprint import pprint

from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from sys import platform
import os
import subprocess
import yaml
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath


class RegisterCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_register(self, args, arguments):
        """
        ::

          Usage:
              register aws yaml
              register aws [FILENAME] [--keep]
              register azure [FILENAME] [--keep]
              register google [FILENAME] [--keep]
              register chameleon [FILENAME] [--keep]


          This command adds the registrarion information the th cloudmesh
          yaml file. The permissions of theFILENAME will also be changed.
          A y/n question will be asked if the files with the filename shoudl
          be deleted after integration

          Arguments:
              FILENAME   a filename in which the cloud credentials are stored

          Options:
              --keep    keeps the file with the filename.

          Description:

            AWS

                AWS dependent on how you downloaded the creadentials will either
                use the filename `credentials.csv` or `accessKey.csv`

                Our command is smart provides some convenience functionality.


                1. If either file is found in ~/Downloads, it is moved to
                   ~/.cloudmesh and the permissions are changed
                2. If such a file already exists there it will ask if it should
                   be overwritten in case the content is not the same
                3. The content of the file will be read to determine if it is
                   likely to be an AWS credential
                4. The credential will be added to the cloudmesh yaml file

            Azure

                Is not yet implemented

            Google

                Is not yet implemented

            Chameleon Cloud

                is not yet implemented
        """

        if arguments.aws:

            # TODO: This code should be moved to AWSRegister

            #
            # Do dynamic loading in AWSRegister as a function
            #
            import selenium as sel
            from cloudmesh.register.AWSRegister import AWSRegister
            #
            # Pandas should not be used, but
            # TODO: change csv
            # import csv
            # the csv code needs to be changed

            import pandas

            if arguments.yaml:


                if platform == "linux" or platform == "linux2":
                    # check if chrome installed
                    try:
                        chrome_ver1 = subprocess.getoutput('google-chrome-stable --version')
                        chrome_ver2 = subprocess.getoutput('google-chrome --version')
                        if 'not found' in chrome_ver1.lower() or 'not found' in chrome_ver2.lower():
                            Console.error("google chrome is not installed")
                            return
                        self.driver = sel.webdriver.Chrome()
                        # TODO: this does not have the return check as the others have?
                        register = AWSRegister(self.driver)
                        register.create_user()
                        credentials_csv_path = Path.home().joinpath('Downloads').joinpath('credentials.csv').resolve()
                        cloudmesh_folder = Path.home().joinpath('.cloudmesh').resolve()
                        os.rename(credentials_csv_path, cloudmesh_folder.joinpath('credentials.csv').resolve())
                        Console.info("credentials.csv moved to ~/.cloudmesh folder")

                        with open("{cm}/cloudmesh4.yaml".format(cm=cloudmesh_folder)) as f:
                            cloudmesh_conf = yaml.load(f, Loader=yaml.FullLoader)

                        creds = pandas.read_csv("{cm}/credentials.csv".format(cm=cloudmesh_folder))

                        cloudmesh_conf['cloudmesh']['cloud']['aws']['credentials']['EC2_ACCESS_ID'] = \
                            creds['Access key ID'][0]
                        cloudmesh_conf['cloudmesh']['cloud']['aws']['credentials']['EC2_SECRET_KEY'] = \
                            creds['Secret access key'][0]

                        with open("{cm}/cloudmesh4.yaml".format(cm=cloudmesh_folder), "w") as f:
                            yaml.dump(cloudmesh_conf, f)

                        Console.info("AWS 'Access Key ID' and 'Secret Access Key' in the cloudmesh4.yaml updated")

                    except sel.common.exceptions.Webself.driverException:
                        Console.error("Chrome geckodriver not installed. Follow these steps for installation: \n"
                                      "1) Download the driver from the following link: \n\t "
                                      "https://sites.google.com/a/chromium.org/chromedriver/downloads \n"
                                      "2) Copy the `chromedriver` to '/usr/bin' \n"
                                      "3) Set the permission using:\n\t"
                                      "'sudo chmod +x /usr/bin/chromedriver'")

                elif platform == "darwin":
                    chrome = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
                    if not chrome.is_file():
                        Console.error("Google chrome is not installed")
                        return
                    try:
                        self.driver = sel.webdriver.Chrome()
                    except sel.common.exceptions.WebDriverException:
                        Console.error("Chrome geckodriver not installed. Follow these steps for installation: \n"
                                      "1) Download the driver from the following link: \n\t "
                                      "https://sites.google.com/a/chromium.org/chromedriver/downloads \n"
                                      "2) Copy the `chromedriver` to '/usr/local/bin' \n"
                                      "3) Set the permission using:\n\t"
                                      "'chmod +x /usr/local/bin/chromedriver'")
                        return
                    register = AWSRegister(self.driver)
                    credentials_csv_path = Path.home().joinpath('Downloads').joinpath('credentials.csv').resolve()
                    cloudmesh_folder = Path.home().joinpath('.cloudmesh').resolve()
                    os.rename(credentials_csv_path, cloudmesh_folder.joinpath('credentials.csv').resolve())
                    Console.info("credentials.csv moved to ~/.cloudmesh folder")

                    with open("{cm}/cloudmesh4.yaml".format(cm=cloudmesh_folder)) as f:
                        cloudmesh_conf = yaml.load(f, Loader=yaml.FullLoader)

                    creds = pandas.read_csv("{cm}/credentials.csv".format(cm=cloudmesh_folder))

                    cloudmesh_conf['cloudmesh']['cloud']['aws']['credentials']['EC2_ACCESS_ID'] = creds['Access key ID'][0]
                    cloudmesh_conf['cloudmesh']['cloud']['aws']['credentials']['EC2_SECRET_KEY'] = creds['Secret access key'][0]

                    with open("{cm}/cloudmesh4.yaml".format(cm=cloudmesh_folder), "w") as f:
                        yaml.dump(cloudmesh_conf, f)

                    Console.info("AWS 'Access Key ID' and 'Secret Access Key' in the cloudmesh4.yaml updated")


                elif platform == "win32":
                    chrome = Path("C:\Program Files (x86)\Google\Chrome\Application\Chrome.exe")
                    if not chrome.is_file():
                        Console.error("Google chrome is not installed")
                        return
                    try:
                        self.driver = sel.webdriver.Chrome()
                    except sel.common.exceptions.WebDriverException:
                        Console.error("Chrome geckodriver not installed. Follow these steps for installation: \n"
                                      "1) Download the driver from the following link: \n\t "
                                      "https://sites.google.com/a/chromium.org/chromedriver/downloads \n"
                                      "2) Copy the `chromedriver` to path, for instance you can add it to the followtin path: \n\t %USERPROFILE%\AppData\Local\Microsoft\WindowsApps")
                        return
                    self.driver = sel.webdriver.Chrome()
                    register = AWSRegister(self.driver)
                    credentials_csv_path = Path.home().joinpath('Downloads').joinpath('credentials.csv').resolve()
                    cloudmesh_folder = Path.home().joinpath('.cloudmesh').resolve()
                    os.rename(credentials_csv_path, cloudmesh_folder.joinpath('credentials.csv').resolve())
                    Console.info("credentials.csv moved to ~/.cloudmesh folder")

                    with open("{cm}/cloudmesh4.yaml".format(cm=cloudmesh_folder)) as f:
                        cloudmesh_conf = yaml.load(f, Loader=yaml.FullLoader)

                    creds = pandas.read_csv("{cm}/credentials.csv".format(cm=cloudmesh_folder))

                    cloudmesh_conf['cloudmesh']['cloud']['aws']['credentials']['EC2_ACCESS_ID'] = creds['Access key ID'][0]
                    cloudmesh_conf['cloudmesh']['cloud']['aws']['credentials']['EC2_SECRET_KEY'] = creds['Secret access key'][0]

                    with open("{cm}/cloudmesh4.yaml".format(cm=cloudmesh_folder), "w") as f:
                        yaml.dump(cloudmesh_conf, f)

                    Console.info("AWS 'Access Key ID' and 'Secret Access Key' in the cloudmesh4.yaml updated")
            else:
                Console.error("not yet implemented")

        elif arguments.azure:
            Console.error("not yet implemented")

        elif arguments.google:

            Console.error("not yet implemented")

        elif arguments.chameleon:

            Console.error("not yet implemented")

        return ""

