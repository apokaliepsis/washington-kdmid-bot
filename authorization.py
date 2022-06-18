from google_doc import Google_Doc
from manager_app import ManagerApp
from captcha import Captcha
from time import sleep
import pickle
import random
import string
from cffi.backend_ctypes import xrange
import base64





class Authorization:
    def authorize(self, user):
        ManagerApp().get_logger().info("Authorization user")
        driver = ManagerApp().get_driver()
        # driver.get("http://washington.kdmid.ru/")
        # driver.find_element_by_xpath("//*[contains(text(),'Войти')]").click()
        # driver.find_element_by_id("LinkButtonA").click()
        # driver.find_element_by_css_selector("#Checkbox").click()
        # driver.find_element_by_css_selector("#Checkbox2").click()
        # driver.find_element_by_id("ButtonNext").click()
        driver.get("http://washington.kdmid.ru/queue/Visitor.aspx")
        # valueRandom = "".join([random.choice(string.ascii_letters) for i in xrange(10)])
        # email = "".join([random.choice(string.ascii_letters) for i in xrange(5)]) + str("@") \
        #         + "".join([random.choice(string.ascii_letters) for i in xrange(5)]) + str(".com")
        ManagerApp().get_logger().info("Filling in fields")
        driver.find_element_by_css_selector("#ctl00_MainContent_txtFam").send_keys(user.get(Google_Doc.surname))
        driver.find_element_by_css_selector("#ctl00_MainContent_txtIm").send_keys(user.get(Google_Doc.name))
        driver.find_element_by_css_selector("#ctl00_MainContent_txtOt").send_keys(user.get(Google_Doc.middle_name))
        driver.find_element_by_css_selector("#ctl00_MainContent_txtTel").send_keys(user.get(Google_Doc.phone))
        driver.find_element_by_css_selector("#ctl00_MainContent_txtEmail").send_keys(user.get(Google_Doc.email))
        birth_date = user.get(Google_Doc.birth_date)
        self.set_birth_date(birth_date)

        # captcha_error = True
        ManagerApp().get_logger().info("Captcha recognition")
        while True:
            captcha_code = Captcha().recognize_captcha()
            captcha_field = driver.find_element_by_id("ctl00_MainContent_txtCode")
            captcha_field.clear()
            captcha_field.send_keys(captcha_code)
            driver.find_element_by_name("ctl00$MainContent$ButtonA").click()
            #if len(driver.find_elements_by_css_selector("#ctl00_MainContent_lblCodeErr")) == 0:
            driver.implicitly_wait(3)
            if len(driver.find_elements_by_xpath("//*[@class='reason_enable']//*[text()='Загранпаспорт']"))>0:
                break
            print("Captcha was entered incorrectly")
            #driver.refresh()
        driver.implicitly_wait(15)
        print("Captcha passed")

    def set_birth_date(self, birth_date):
        driver = ManagerApp().get_driver()

        birth_date__split = str(birth_date).split(".")
        day = birth_date__split[0]
        month = birth_date__split[1]
        year = birth_date__split[2]
        driver.find_element_by_css_selector("#ctl00_MainContent_DDL_Day").click()
        driver.find_element_by_xpath("//*[@name='ctl00$MainContent$DDL_Day']//*[@value='%s']" % day).click()

        driver.find_element_by_css_selector("#ctl00_MainContent_DDL_Month").click()
        driver.find_element_by_xpath("//*[@name='ctl00$MainContent$DDL_Month']//*[@value='%s']" % month).click()

        driver.find_element_by_css_selector("#ctl00_MainContent_TextBox_Year").send_keys(year)