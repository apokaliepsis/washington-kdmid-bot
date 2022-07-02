from time import sleep


from network_file.google_doc import Google_Doc

from captcha import Captcha

import concurrent.futures


class Authorization:

    start_page = "http://washington.kdmid.ru/queue/Visitor.aspx"
    def authorize(self, client):
        from manager.manager_app import ManagerApp
        ManagerApp.logger_client.info(str(client.get(Google_Doc.phone))+": Authorization client")
        driver = ManagerApp().get_driver()
        # driver.get("http://washington.kdmid.ru/")
        # driver.find_element_by_xpath("//*[contains(text(),'Войти')]").click()
        # driver.find_element_by_id("LinkButtonA").click()
        # driver.find_element_by_css_selector("#Checkbox").click()
        # driver.find_element_by_css_selector("#Checkbox2").click()
        # driver.find_element_by_id("ButtonNext").click()
        driver.get(Authorization.start_page)
        # valueRandom = "".join([random.choice(string.ascii_letters) for i in xrange(10)])
        # email = "".join([random.choice(string.ascii_letters) for i in xrange(5)]) + str("@") \
        #         + "".join([random.choice(string.ascii_letters) for i in xrange(5)]) + str(".com")
        ManagerApp.logger_main.info(str(client.get(Google_Doc.phone))+": Filling in fields")
        driver.find_element_by_css_selector("#ctl00_MainContent_txtFam").send_keys(client.get(Google_Doc.surname))
        driver.find_element_by_css_selector("#ctl00_MainContent_txtIm").send_keys(client.get(Google_Doc.name))
        driver.find_element_by_css_selector("#ctl00_MainContent_txtOt").send_keys(client.get(Google_Doc.middle_name))
        driver.find_element_by_css_selector("#ctl00_MainContent_txtTel").send_keys(client.get(Google_Doc.phone))
        driver.find_element_by_css_selector("#ctl00_MainContent_txtEmail").send_keys(client.get(Google_Doc.email))
        birth_date = client.get(Google_Doc.birth_date)
        self.set_birth_date(birth_date)

        # captcha_error = True
        while True:
            ManagerApp.logger_client.info(str(client.get(Google_Doc.phone))+": Begin recognize_captcha")
            #captcha_code = Captcha().recognize_captcha()
            captcha_code:str
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(Captcha().recognize_captcha)
                captcha_code = future.result()
                future.done()
            ManagerApp.logger_client.info(str(client.get(Google_Doc.phone))+": captcha_code="+ str(captcha_code))
            captcha_field = driver.find_element_by_css_selector("#ctl00_MainContent_txtCode")
            captcha_field.clear()

            captcha_field.send_keys(captcha_code)
            driver.find_element_by_name("ctl00$MainContent$ButtonA").click()
            #if len(driver.find_elements_by_css_selector("#ctl00_MainContent_lblCodeErr")) == 0:
            driver.implicitly_wait(3)
            if len(driver.find_elements_by_xpath("//*[@class='reason_enable']//*[text()='Загранпаспорт']"))>0:
                break
            ManagerApp.logger_client.info(str(client.get(Google_Doc.phone))+": Captcha was entered incorrectly")
            #driver.refresh()
        driver.implicitly_wait(ManagerApp.time_implicit_wait)
        ManagerApp.logger_client.info(str(client.get(Google_Doc.phone))+": Captcha passed")

    def set_birth_date(self, birth_date):
        from manager.manager_app import ManagerApp
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