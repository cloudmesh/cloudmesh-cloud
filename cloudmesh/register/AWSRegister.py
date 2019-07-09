from time import sleep
import random
import getpass
from time import sleep
from cloudmesh.common.console import Console
import selenium as sel

class AWSRegister(object):

    def __init__(self, driver):
        self.driver = driver

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


    def create_user(self, driver):
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
