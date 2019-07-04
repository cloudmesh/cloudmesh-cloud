from pprint import pprint

from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from sys import platform
from shell import shell
import selenium as sel
from selenium import webdriver
import getpass
from time import sleep
import random
from pathlib import Path, PurePath, PurePosixPath,PureWindowsPath
import yaml
import pandas
import os

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
            if arguments.yaml:
                if platform == "linux" or platform == "linux2":
                    # check if chrome installed
                    try:
                        chrome_ver1 = shell('google-chrome-stable --version')
                        chrome_ver2 = shell('google-chrome --version')
                        self.driver = sel.webdriver.Chrome()
                        self.create_user()
                        credentials_csv_path = '{Downloads}/credentials.csv'.format(Downloads=PurePosixPath(Path.home()).joinpath('Downloads').as_posix())
                        cloudmesh_folder = '{Home}/.cloudmesh'.format(Home=Path.home().as_posix())
                        shell('mv {cred} {cm}'.format(cred=credentials_csv_path,cm=cloudmesh_folder))
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

                    except FileNotFoundError:
                        Console.error("google chrome is not installed")
                    except sel.common.exceptions.Webself.driverException:
                        Console.error("Chrome geckodriver not installed. Follow these steps for installation: \n"
                                      "1) Download the driver from the following link: \n\t "
                                      "https://sites.google.com/a/chromium.org/chromedriver/downloads \n"
                                      "2) Copy the `chromedriver` to '/usr/bin' \n"
                                      "3) Set the permission using:\n\t"
                                      "'sudo chmod +x /usr/bin/chromedriver'")

                elif platform == "darwin":
                    Console.error("aws registration is not yet tested in macOS")
                elif platform == "win32":
                    chrome = Path("C:\Program Files (x86)\Google\Chrome\Application\Chrome.exe")
                    if not chrome.is_file():
                        Console.error("Google chrome is not installed")
                    try:
                        self.driver = sel.webdriver.Chrome()
                    except sel.common.exceptions.WebDriverException:
                        Console.error("Chrome geckodriver not installed. Follow these steps for installation: \n"
                                      "1) Download the driver from the following link: \n\t "
                                      "https://sites.google.com/a/chromium.org/chromedriver/downloads \n"
                                      "2) Copy the `chromedriver` to path, for instance you can add it to the followtin path: \n\t %USERPROFILE%\AppData\Local\Microsoft\WindowsApps")
                    self.create_user()
                    credentials_csv_path = PureWindowsPath('{Downloads}/credentials.csv'.format(
                        Downloads=PurePosixPath(Path.home()).joinpath('Downloads')))
                    cloudmesh_folder = PureWindowsPath('{Home}/.cloudmesh'.format(Home=Path.home().as_posix()))
                    os.system('move {cred} {cm}'.format(cred=credentials_csv_path, cm=cloudmesh_folder))
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

    def slow_typer(self,element, text):
        for character in text:
            element.send_keys(character)
            sleep(random.random() * 0.05)

    def check_captcha(self):
        if "Type the characters seen in the image below" in self.driver.page_source:
            text = input("Captcha encountered. Please enter the captcha and press Submit then press Enter to continue")
            while (text != ""):
                text = input(
                    "Captcha encountered. Please enter the captcha and press Submit then press Enter to continue")

    def create_user(self):
        email = input("Enter your email: ")
        passw = getpass.getpass("Enter your password: ")
        self.driver.get("https://console.aws.amazon.com/iam/home#/users")
        assert "Amazon Web Services" in self.driver.title, "Unexpected login page, aborting"
        sleep(1)
        self.driver.find_element_by_id("resolving_input").send_keys(email)
        self.driver.find_element_by_id("next_button").click()
        self.check_captcha()
        sleep(1)
        self.driver.find_element_by_id("password").send_keys(passw)
        self.driver.find_element_by_id("signin_button").click()
        sleep(1)
        self.check_captcha()
        # adding cloudmesh user
        self.driver.find_element_by_link_text("Add user").click()
        sleep(1)
        self.driver.find_element_by_id("awsui-textfield-17").send_keys("cloudmesh")
        self.driver.find_element_by_name("accessKey").click()
        sleep(1)
        self.driver.find_element_by_class_name("wizard-next-button").click()
        sleep(1)
        self.driver.find_element_by_class_name("awsui-util-pt-s").click()
        sleep(1)
        self.driver.find_element_by_xpath("//awsui-textfield[@ng-model='createGroupModal.groupName']/input").send_keys(
            "cloudmesh")
        sleep(1)
        self.driver.find_element_by_xpath('//*/policies-table//table-search//search/div/input').send_keys(
            "AmazonEC2FullAccess")
        sleep(1)
        self.driver.find_element_by_xpath(
            '//div[@data-item-id="arn:aws:iam::aws:policy/AmazonEC2FullAccess"]//awsui-checkbox//div').click()
        sleep(1)
        self.driver.find_element_by_xpath("//awsui-button[@click-tracker='CreateGroup']").click()
        Console.info("'cloudmesh' group created")
        sleep(1)
        self.driver.find_element_by_class_name("wizard-next-button").click()
        sleep(1)
        self.driver.find_element_by_class_name("wizard-next-button").click()
        Console.info("'cloudmesh' user created")
        sleep(1)
        self.driver.find_element_by_class_name("wizard-next-button").click()
        sleep(1)
        self.driver.find_element_by_xpath("//awsui-button[@text='Download .csv']").click()
        Console.info("credentials.csv downloaded")
        sleep(2)
        self.driver.find_element_by_xpath("//awsui-button[@text='Close']").click()
        sleep(4)
