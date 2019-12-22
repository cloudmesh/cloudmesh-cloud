import random
import getpass
from time import sleep
from cloudmesh.common.console import Console
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from sys import platform
import os
import subprocess
from pathlib import Path
import pandas
from cloudmesh.configuration.Config import Config


class AWSRegister(object):

    def __init__(self, cloud='aws'):

        self.config = Config()
        self.credentials = self.config[f'cloudmesh.cloud.{cloud}.credentials']

    def set_credentials(self, creds):
        self.credentials['EC2_ACCESS_ID'] = creds['Access key ID'][0]
        self.credentials['EC2_SECRET_KEY'] = creds['Secret access key'][0]
        self.config.save()

    def register(self, cloud='aws'):
        if platform == "linux" or platform == "linux2":
            # check if chrome installed

            chrome_ver1 = subprocess.getoutput('google-chrome-stable --version')
            chrome_ver2 = subprocess.getoutput('google-chrome --version')

            if 'not found' in chrome_ver1.lower() or 'not found' in chrome_ver2.lower():
                Console.error("google chrome is not installed")
                return
            # self.driver = webdriver.Chrome()
            try:
                self.driver = webdriver.Chrome()
                # register = AWSRegister(self.driver)
            except WebDriverException as e:
                Console.error(e)

                Console.error(
                    "Chrome geckodriver not installed. Follow these steps for installation: \n"
                    "1) Download the driver from the following link: \n\t "
                    "https://sites.google.com/a/chromium.org/chromedriver/downloads \n"
                    "2) Copy the `chromedriver` to '/usr/bin' \n"
                    "3) Set the permission using:\n\t"
                    "'sudo chmod +x /usr/bin/chromedriver'")

                return

            credentials_file_name = self.create_user()

            credentials_csv_path = Path.home().joinpath('Downloads').joinpath(
                credentials_file_name).resolve()
            cloudmesh_folder = Path.home().joinpath('.cloudmesh').resolve()

            os.rename(credentials_csv_path, cloudmesh_folder.joinpath(
                credentials_file_name).resolve())
            Console.info("{filename} moved to ~/.cloudmesh folder".format(
                filename=credentials_file_name))

            creds = pandas.read_csv(
                "{cm}/{filename}".format(cm=cloudmesh_folder,
                                         filename=credentials_file_name))

            self.set_credentials(creds)

            self.config.save()

            Console.info(
                "AWS 'Access Key ID' and 'Secret Access Key' in the cloudmesh.yaml updated")

        elif platform == "darwin":
            chrome = Path(
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
            if not chrome.is_file():
                Console.error("Google chrome is not installed")
                return
            try:
                self.driver = webdriver.Chrome()
            except WebDriverException as e:
                Console.error(e)
                Console.error(
                    "Chrome geckodriver not installed. Follow these steps for installation: \n"
                    "1) Download the driver from the following link: \n\t "
                    "https://sites.google.com/a/chromium.org/chromedriver/downloads \n"
                    "2) Copy the `chromedriver` to '/usr/local/bin' \n"
                    "3) Set the permission using:\n\t"
                    "'chmod +x /usr/local/bin/chromedriver'")
                return

            credentials_file_name = self.create_user()
            credentials_csv_path = Path.home().joinpath('Downloads').joinpath(
                credentials_file_name).resolve()
            # check if the DOwanloaded file exists
            # Path("~/.cloudmesh/{credentials_file_name}).resolve()

            cloudmesh_folder = Path.home().joinpath('.cloudmesh').resolve()
            os.rename(credentials_csv_path, cloudmesh_folder.joinpath(
                credentials_file_name).resolve())
            Console.info(
                f"{credentials_file_name} moved to ~/.cloudmesh folder")

            creds = pandas.read_csv(
                "{cm}/{filename}".format(cm=cloudmesh_folder,
                                         filename=credentials_file_name))

            self.set_credentials(creds)

            Console.info(
                "AWS 'Access Key ID' and 'Secret Access Key' in the cloudmesh.yaml updated")


        elif platform == "win32":
            chrome = Path(
                "C:\Program Files (x86)\Google\Chrome\Application\Chrome.exe")
            if not chrome.is_file():
                Console.error("Google chrome is not installed")
                return
            try:
                self.driver = webdriver.Chrome()
            except WebDriverException as e:
                Console.error(e)
                Console.error(
                    "Chrome geckodriver not installed. Follow these steps for installation: \n"
                    "1) Download the driver from the following link: \n\t "
                    "https://sites.google.com/a/chromium.org/chromedriver/downloads \n"
                    "2) Copy the `chromedriver` to path, for instance you can add "
                    "it to the followtin path: "
                    "\n\t %USERPROFILE%\\AppData\\Local\\Microsoft\\WindowsApps")
                return
            credentials_file_name = self.create_user()

            credentials_csv_path = Path.home().joinpath('Downloads').joinpath(
                credentials_file_name).resolve()
            cloudmesh_folder = Path.home().joinpath('.cloudmesh').resolve()
            os.rename(credentials_csv_path, cloudmesh_folder.joinpath(
                credentials_file_name).resolve())

            Console.info(
                f"{credentials_file_name} moved to ~/.cloudmesh folder")

            creds = pandas.read_csv(
                "{cm}/{filename}".format(cm=cloudmesh_folder,
                                         filename=credentials_file_name))

            self.set_credentials(creds)

            Console.info(
                "AWS 'Access Key ID' and 'Secret Access Key' in the cloudmesh.yaml updated")

    def slow_typer(self, element, text):
        for character in text:
            element.send_keys(character)
            sleep(random.random() * 0.05)

    def check_captcha(self):
        if "Type the characters seen in the image below" in self.driver.page_source:
            text = input(
                "Captcha encountered. Please enter the captcha and press Submit then press Enter to continue")
            while (text != ""):
                text = input(
                    "Captcha encountered. Please enter the captcha and press Submit then press Enter to continue")

    def create_user(self):
        '''
        Creates the user or if the user exists creates another access key
        :return: the name of the file containing the access key
        '''
        email = input("Enter your email: ")
        passw = getpass.getpass("Enter your password: ")
        self.driver.get("https://console.aws.amazon.com/iam/home#/users")
        assert "Amazon Web Services" in self.driver.title, "Unexpected login page, aborting"
        sleep(1.5)
        self.driver.find_element_by_id("resolving_input").send_keys(email)
        self.driver.find_element_by_id("next_button").click()
        sleep(1.5)
        self.check_captcha()

        self.driver.find_element_by_id("password").send_keys(passw)
        self.driver.find_element_by_id("signin_button").click()
        sleep(1.5)
        self.check_captcha()

        # adding cloudmesh user
        if self.user_exists():
            self.create_accesskey_on_current_account()
            return "accessKeys.csv"

        self.driver.find_element_by_link_text("Add user").click()
        sleep(1.5)

        self.driver.find_element_by_id("awsui-textfield-17").send_keys(
            "cloudmesh")
        self.driver.find_element_by_name("accessKey").click()
        sleep(1.5)

        self.driver.find_element_by_class_name("wizard-next-button").click()
        sleep(1.5)

        self.driver.find_element_by_class_name("awsui-util-pt-s").click()
        sleep(1.5)

        self.driver.find_element_by_xpath(
            "//awsui-textfield[@ng-model='createGroupModal.groupName']/input").send_keys(
            "cloudmesh")
        sleep(1.5)
        self.driver.find_element_by_xpath(
            '//*/policies-table//table-search//search/div/input').send_keys(
            "AmazonEC2FullAccess")
        sleep(1.5)
        self.driver.find_element_by_xpath(
            '//div[@data-item-id="arn:aws:iam::aws:policy/AmazonEC2FullAccess"]//awsui-checkbox//div').click()
        sleep(1.5)
        self.driver.find_element_by_xpath(
            "//awsui-button[@click-tracker='CreateGroup']").click()
        sleep(1.5)
        Console.info("'cloudmesh' group created")

        self.driver.find_element_by_class_name("wizard-next-button").click()
        sleep(1.5)
        self.driver.find_element_by_class_name("wizard-next-button").click()
        sleep(1.5)

        Console.info("'cloudmesh' user created")
        self.driver.find_element_by_class_name("wizard-next-button").click()
        sleep(1.5)
        self.driver.find_element_by_xpath(
            "//awsui-button[@text='Download .csv']").click()
        Console.info("credentials.csv downloaded")
        sleep(2)

        self.driver.find_element_by_xpath(
            "//awsui-button[@text='Close']").click()
        sleep(4)
        return "credentials.csv"

    def user_exists(self):
        sleep(1.5)
        return len(self.driver.find_elements_by_link_text("cloudmesh")) > 0

    def create_accesskey_on_current_account(self):
        self.driver.find_element_by_xpath(
            '//a[@href="#/users/cloudmesh"]').click()
        sleep(1.5)

        self.driver.find_element_by_link_text("Security credentials").click()
        sleep(1.5)

        while len(self.driver.find_elements_by_xpath(
            '//span[text()="Make inactive"]')) == 2:
            input(
                "Two access keys already exist for the user, remove one manually before creating another one and press Enter")

        self.driver.find_element_by_xpath(
            '//button[.//span[text()="Create access key"]]').click()
        sleep(1.5)
        self.driver.find_element_by_xpath(
            '//*[@id="modal-container"]//awsui-button[contains(@text,"Download .csv file")]').click()
        sleep(1.5)

        Console.info("accessKeys.csv downloaded")
