import random

from manager.control import Control
from network_file.google_doc import Google_Doc
from manager.manager_app import ManagerApp
from datetime import datetime, timedelta
import time
from time import sleep


class Calendar_Page:
    table_xpath = '//table[@id="ctl00_MainContent_RadioButtonList1"]'

    def get_month_by_number(self, num):
        months = {1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель', 5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
                  9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'}
        return months[num]

    def get_month_sclonen_by_number(self, num):
        months = {"01": 'января', "02": 'февраля', "03": 'марта', "04": 'апреля', "05": 'мая', "06": 'июня',
                  "07": 'июля', "08": 'августа',
                  "09": 'сентября', "10": 'октября', "11": 'ноября', "12": 'декабря'}
        return months[num]

    def get_number_by_month(self, month):
        months = {'Январь': 1, 'Февраль': 2, 'Март': 3, 'Апрель': 4, 'Май': 5, 'Июнь': 6, 'Июль': 7, 'Август': 8,
                  'Сентябрь': 9, 'Октябрь': 10, 'Ноябрь': 11, 'Декабрь': 12}
        print(months[month])
        return months[month]

    def get_current_month_and_year(self):
        driver = ManagerApp().get_driver()
        text_date = driver.find_element_by_css_selector(
            "#ctl00_MainContent_Calendar > tbody > tr:nth-child(1) > td > table > tbody > tr > td:nth-child(2)").text
        print(text_date)
        return text_date

    def get_current_date(self):
        text_date = self.get_current_month_and_year()
        month = self.get_number_by_month(str(text_date).split(" ")[0])
        year = str(text_date).split(" ")[1]
        return "01." + str(month) + "." + str(year)

    def reset_days_date(self, user_date):
        user_date = datetime.strptime(user_date, '%d.%m.%Y')
        newdatetime = user_date.replace(day=1)
        return newdatetime.strftime("%d.%m.%Y")

    def get_days_from_many_dates(self, many_dates):
        dates = []
        if many_dates.__contains__("-"):
            str_d1 = str(many_dates).split("-")[0].strip()
            str_d2 = str(many_dates).split("-")[1].strip()

            d1 = datetime.strptime(str_d1, "%d.%m.%Y")
            d2 = datetime.strptime(str_d2, "%d.%m.%Y")

            delta = d2 - d1
            for i in range(delta.days + 1):
                day = d1 + timedelta(days=i)
                day = datetime.strptime(str(day), '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y')
                dates.append(day)
                print(day)
        if many_dates.__contains__(","):
            data_split = many_dates.split(",")
            for i in data_split:
                dates.append(i.strip())
        return dates

    def get_radiobutton_id_list(self):
        radiobutton_list = []
        driver = ManagerApp().get_driver()
        table = driver.find_element_by_xpath('%s' % self.table_xpath)
        for row in table.find_elements_by_xpath("//tr//td//label"):
            element = row.text
            print(element)
            radiobutton_list.append(element)
        # random_id = random.choice(radiobutton_list)
        # print(random_id)
        return radiobutton_list

    def set_date_to_calendar(self, date_order, client_data, process_queue_shared):
        driver = ManagerApp().get_driver()
        user_default_date = time.strptime(self.reset_days_date(date_order), "%d.%m.%Y")
        print(user_default_date)
        while True:
            current_date = time.strptime(self.get_current_date(), "%d.%m.%Y")
            if current_date > user_default_date:
                print("Найденный месяц больше требуемого")
                ManagerApp.logger_client.info("Click by last month")
                driver.find_element_by_xpath("//*[@title='Перейти к предыдущему месяцу']").click()
            elif current_date < user_default_date:
                print("Найденный месяц меньше требуемого")
                ManagerApp.logger_client.info("Click by next month")
                try:
                    driver.find_element_by_xpath("//*[@title='Перейти к следующему месяцу']").click()
                except:
                    ManagerApp.logger_client.warning("Calendar is not available!. Restart process")
                    ManagerApp().get_driver().quit()
                    Control().get_client_order(client_data, process_queue_shared)

            else:
                print("Найденный месяц равен требуемому")
                break
        self.click_by_day(date_order)

    def select_specific_slot(self, client, process_queue_shared):

        phone_client = client.get(Google_Doc.phone)
        #date_order = Control().get_value_client_from_clients_data(Google_Doc.order_date, phone_client)
        date_order = client.get(Google_Doc.order_date)
        ManagerApp.logger_client.info(str(client.get(Google_Doc.phone))
                                            +": Select specific slot: "+"\n"
                                            +"client_data=" + str(client)+"\n"
                                            +"phone_client="+str(phone_client)+"\n"
                                            +"date_order="+str(date_order))
        if str(date_order).__contains__("-") or str(date_order).__contains__(","):
            dates = self.get_days_from_many_dates(date_order)
            print(dates)
            is_exist_free_slot = False
            while is_exist_free_slot == False:
                for day in dates:
                    self.set_date_to_calendar(day, client, process_queue_shared)
                    is_exist_free_slot = self.wait_free_slot(client, process_queue_shared, True)
        else:
            self.set_date_to_calendar(date_order, client, process_queue_shared)
            self.wait_free_slot(client, process_queue_shared, False)

        self.click_by_free_slot()

    def click_by_free_slot(self):
        driver = ManagerApp().get_driver()
        radiobutton_list = self.get_radiobutton_id_list()
        choice = random.choice(radiobutton_list)
        ManagerApp.logger_client.info("Click by day: " + str(choice))
        driver.find_element_by_xpath("//*[contains(text(),'%s')]" % choice).click()

    def click_by_day(self, user_date):
        driver = ManagerApp().get_driver()
        month = str(self.get_month_sclonen_by_number(str(user_date).split(".")[1]))
        day = str(user_date).split(".")[0]
        date = month + " " + day
        ManagerApp.logger_client.info("Click by day: " + str(date))
        driver.find_element_by_xpath("//*[contains(@title,'%s')]" % date).click()

    def wait_free_slot(self, client_data, process_queue_shared, is_multidates: bool):
        try:
            driver = ManagerApp().get_driver()
            phone = str(client_data.get(Google_Doc.phone))
            driver.implicitly_wait(1)
            time_refresh_page_wait = int(ManagerApp.get_value_from_config("TIME_REFRESH_PAGE_WAIT"))
            if is_multidates == False:
                while len(driver.find_elements_by_xpath(self.table_xpath)) == 0:
                    ManagerApp.logger_client.info(
                        phone + ": No available slots. We wait " + str(time_refresh_page_wait) + " seconds")
                    time_wait = random.randint(time_refresh_page_wait - 20, time_refresh_page_wait + 20)
                    ManagerApp.logger_client.info(phone + ": Random time set " + str(time_wait))
                    sleep(time_wait)
                    ManagerApp.logger_client.info(phone + ": Refresh page")
                    driver.refresh()
                    if len(driver.find_elements_by_id("ctl00_MainContent_Calendar")) == 0:
                        ManagerApp.logger_client.info(phone + ": Calendar not found. Refreshing the page")

                        driver.implicitly_wait(ManagerApp.time_implicit_wait)
                        Control().get_client_order(client_data, process_queue_shared)
                    if len(driver.find_elements_by_xpath("//*[contains(text(), ' Почему так случилось?')]")) > 0:
                        ManagerApp.logger_client.warning("Найдена страница блокировки!")
                        # driver.delete_all_cookies()
                        ManagerApp().quit_driver()
                        Control().get_client_order(client_data, process_queue_shared)
            elif is_multidates == True:
                if len(driver.find_elements_by_xpath(self.table_xpath)) > 0:
                    return True
                else:
                    sleep(random.randint(time_refresh_page_wait - 20, time_refresh_page_wait + 20))
                    ManagerApp.logger_client.info(
                        phone + ": No available slots. We wait " + str(time_refresh_page_wait) + " seconds")
                    ManagerApp.logger_client.info(phone + ": Refresh page")
                    driver.refresh()
                is_exist_free_slot = len(driver.find_elements_by_xpath(self.table_xpath)) > 0
                driver.implicitly_wait(ManagerApp.time_implicit_wait)
                return is_exist_free_slot
            driver.implicitly_wait(ManagerApp.time_implicit_wait)
        except Exception as e:
            ManagerApp.logger_client.error("Error client waiting: "+str(e))
        ManagerApp.logger_client.info("Exit from loop waiting")

    def click_by_make_order(self):
        ManagerApp.logger_client.info("Click by \"Make order\"")
        driver = ManagerApp().get_driver()
        driver.find_element_by_name("ctl00$MainContent$Button1").click()

    def click_by_print(self):

        ManagerApp.logger_client.info("Save order document as pdf")
        driver = ManagerApp().get_driver()

        driver.find_element_by_xpath("//*[@name='ctl00$MainContent$Button1' and @value='Печать']").click()