import _thread
import glob

import multiprocessing
import shutil
import subprocess
import sys
from multiprocessing import Process
import os
import random
import re
import string
from time import sleep

import pygsheets
from cffi.backend_ctypes import xrange
from dateutil.parser import parse
import urllib.request

from loguru import logger
from memory_profiler import profile

import starter_bot
from starter_bot import start_bot
from data_base import Data_Base
from manager.manager_app import ManagerApp
from page.authorization import Authorization
from page.consul_services import Consul_Services

from network_file.google_doc import Google_Doc


class Control:
    process_queue_shared = multiprocessing.Manager().list()
    thread = "ClientThread_"
    __client_data_list: dict = None

    def get_client_data(self):
        client_data: [] = Google_Doc().get_google_doc_data()
        ManagerApp.logger_main.info("Client data: {}".format(client_data))

        return client_data

    def control_client_process(self, process_queue_shared, client, driver):
        phone = str(client.get(Google_Doc.phone))
        ManagerApp.logger_client.info("{}: Start Control_Client_Process: queue={}".format(phone, process_queue_shared))
        try:
            while True:
                #print("Loop Control_Client_Process")
                for client_process in process_queue_shared:
                    if str(client_process.get("PHONE")) == phone and client_process.get("ACTIVE") == 0:
                        ManagerApp.logger_client.info("Close process for {}".format(phone))
                        # driver.close()
                        # Google_Doc.delete_row_from_doc(phone)
                        Data_Base.execute_process("delete from sessions where phone='%s'" % phone)
                        driver.quit()
                        ManagerApp.logger_client.info("Quit driver for {}".format(phone))
                        # process_queue.remove(client_process)
                        # Control.execute_bash_command()
                        _thread.interrupt_main()
                sleep(5)
        except Exception as e:
            ManagerApp.logger_client.warning("{}: Error control_client_process!".format(phone))
            ManagerApp.logger_client.warning("{}: {}".format(phone, e))

    def get_name_surname_from_client(self, client):
        return str(client.get(Google_Doc.name) + " " + client.get(Google_Doc.surname))

    def get_client_order(self, client, process_queue_shared):
        from page.calendar_page import Calendar_Page
        try:
            if self.check_valid(client):
                ManagerApp.logger_client.info(
                    "Started process for {}".format(self.get_name_surname_from_client(client)))
                ManagerApp().set_ip_poxy(ManagerApp.get_json_data()["proxy_url"])
                # ManagerApp().set_ip_poxy("socks5://LCjFKu:kVN3UD@186.65.115.27:9980")
                driver = ManagerApp().get_driver()
                Control().add_sessions(client)
                pid = driver.service.process.pid
                print("PID=", pid)
                Control().delete_client_from_process_queue_shared(client, process_queue_shared)
                process_queue_shared.append({"PHONE": client.get(Google_Doc.phone), "ACTIVE": 1, "PID": pid})

                control_client_activity_process = Process(target=Control().control_client_process,
                                                          name="Control_Client_Process_" + str(
                                                              client.get(Google_Doc.phone)),
                                                          args=(process_queue_shared, client, driver))
                control_client_activity_process.start()

                ###ManagerApp().set_ip_poxy("socks5://4sdBGU:E3F6K7@181.177.86.241:9526")
                ###ManagerApp().set_ip_poxy("socks5://70KAot:7u6J69@hub-us-6-1.litport.net:5337")
                ###ManagerApp().set_ip_poxy("socks5://LCjFKu:kVN3UD@186.65.115.27:9980")
                ###ManagerApp().set_ip_poxy("socks5://weTPxd:jzzc7M@hub-us-6-1.litport.net:5512")

                Authorization().authorize(client)
                Consul_Services().go_to_for_get_passport(client)
                Calendar_Page().select_specific_slot(client, process_queue_shared)
                Calendar_Page().click_by_make_order()
                driver.implicitly_wait(600)
                Calendar_Page().click_by_print()
                order_file_path = self.save_current_page_as_pdf(client)
                driver.implicitly_wait(ManagerApp.time_implicit_wait)
                starter_bot.send_file(order_file_path, "873327794")

                os.remove(order_file_path)
                Google_Doc().delete_row_gspread(client.get(Google_Doc.phone))
                ManagerApp().quit_driver()
                self.delete_client_from_process_queue_shared(client, process_queue_shared)
                self.delete_client_from_sessions(client)
                control_client_activity_process.kill()
                ManagerApp.logger_client.info("{}: Successfully".format(client.get(Google_Doc.phone)))
                sys.exit()
            else:
                ManagerApp.logger_main.warning("Incorrect client data: {}".format(client))
        except Exception as e:
            ManagerApp.logger_main.error("Unexpected error: {}\nRestart client thread".format(e))
            for index, client_process in enumerate(process_queue_shared):
                if client_process["PHONE"] == client.get(Google_Doc.phone):
                    client_process["ACTIVE"] = 0
                    process_queue_shared[index] = client_process
            ManagerApp().quit_driver()
            sleep(5)
            client = self.get_client_from_clients_data(client.get(Google_Doc.phone))
            self.get_client_order(client, process_queue_shared)

    def delete_client_from_process_queue_shared(self, client, process_queue_shared):
        for item in process_queue_shared:
            if client.get(Google_Doc.phone) in item.values():
                ManagerApp.logger_client.info("Delete client from process_queue_shared")
                process_queue_shared.remove(item)

    def delete_client_from_sessions(self, client):
        ManagerApp.logger_main.info("Delete from sessions client: {}".format(client))
        fio = str(client.get(Google_Doc.name)) + " " + str(client.get(Google_Doc.surname))
        Data_Base.execute_process("delete from sessions where fio='%s'" % fio)

    @logger.catch()
    def run_main(self):
        self.execute_bash_command("pkill -9 -f chromedriver")

        Control().delete_sessions()
        Control().delete_temp_files()
        Control().enable_monitoring()
        Control().create_dir_temp()

        bot_process = Process(target=start_bot, name="Bot", args=(Control.process_queue_shared,))
        bot_process.start()
        Control.__client_data_list = Google_Doc().get_google_doc_data()

        while True:
            try:
                if int(self.get_status_monitoring()) == 1:
                    # self.check_available_site()
                    if int(self.get_status_monitoring()) == 1 and Control.__client_data_list is not None and len(
                            Control.__client_data_list) > 0:
                        self.start_clients_threads(self.get_client_data())
                    Control.__client_data_list = Google_Doc().get_google_doc_data()
                    self.control_sessions_queue()
                sleep(10)


            except Exception as e:
                time_wait = 10
                ManagerApp.logger_main.error("Network problems. Wait %s seconds" % str(time_wait))
                ManagerApp.logger_main.error(e)
                sleep(time_wait)
    def get_status_monitoring(self):
        return Data_Base.get_data_by_query("select* from settings")[0].get("MONITORING_STATUS")

    def enable_monitoring(self):
        ManagerApp.logger_main.info("Enable monitoring")
        return Data_Base.execute_process("update settings set monitoring_status=1")

    def disable_monitoring(self):
        ManagerApp.logger_main.info("Disable monitoring")
        return Data_Base.execute_process("update settings set monitoring_status=0")

    def control_sessions_queue(self):
        try:
            ManagerApp.logger_main.info("Running process: {}".format(multiprocessing.active_children()))
            ManagerApp.logger_main.info(
                "Control sessions queue: process_queue_shared={}".format(Control.process_queue_shared))
            for client in Control.process_queue_shared:
                # print("control_sessions: client=", client)
                if client["ACTIVE"] == 0:
                    phone = str(client.get("PHONE"))
                    # print("control_sessions_db: ", phone)
                    for p in multiprocessing.active_children():
                        print(p.name)
                        if p.name.__contains__(Control.thread) and p.name.__contains__(phone):
                            ManagerApp.logger_main.info("Session_Conctrol: Process {} kill".format(p.name))
                            p.kill()
                            self.execute_bash_command("kill -9 {}".format(client.get("PID")))
                            Control.process_queue_shared.remove(client)
            # ManagerApp.logger_main.info("control_sessions: process_queue_shared after="+ str(Control.process_queue_shared))
        except Exception as e:
            ManagerApp.logger_main.warning(str(e))

    def stop_all_process(self):
        ManagerApp.logger_main.info("Stop all clients process...")
        for p in multiprocessing.active_children():
            print(p.name)
            if p.name.__contains__(Control.thread):
                p.kill()
        Control.process_queue_shared = multiprocessing.Manager().list()
        ManagerApp.logger_main.info(
            "Process_queue_shared={}".format(Control.process_queue_shared))
        self.delete_sessions()
        self.disable_monitoring()
        self.execute_bash_command("pkill -9 -f chromedriver")
        self.execute_bash_command("pkill -9 -f chrome")
        ManagerApp.logger_main.info("All client processes are killed")

    def delete_sessions(self):
        ManagerApp.logger_main.info("Delete sessions")
        Data_Base.execute_process("delete from sessions")
        # print("select* from sessions=", Data_Base.execute_select_query("select* from sessions"))

    def start_clients_threads(self, client_data_list):
        ManagerApp.logger_main.info("Start clients threads...")
        for client in client_data_list:
            if self.check_exist_process(client.get(Google_Doc.phone)) == False and int(self.get_status_monitoring()) == 1:
                name_process = "ClientThread_{}".format(client.get(Google_Doc.phone))
                ManagerApp.logger_main.info("Started process for {}".format(self.get_name_surname_from_client(client)))
                p1 = Process(target=self.get_client_order, name=name_process,
                             args=(client, Control.process_queue_shared))
                p1.start()
                ManagerApp.logger_main.info("Start {}".format(name_process))
            sleep(5)

    def add_sessions(self, client):
        fio = self.get_name_surname_from_client(client)
        order_date = client.get(Google_Doc.order_date)
        phone = client.get(Google_Doc.phone)
        active = 1
        if len(Data_Base.get_data_by_query("select* from sessions where phone='%s'" % phone)) > 0:
            Data_Base.execute_process("delete from sessions where phone='%s'" % phone)
        Data_Base.execute_process(
            "insert into sessions (fio, order_date, phone, active) values ('%s', '%s', '%s', '%s')" % (
                fio, order_date, phone, active))

    def stop_process_by_phone(self, phone):
        try:
            for p in multiprocessing.active_children():
                if p.name.__contains__(Control.thread) and p.name.__contains__(phone):
                    p.terminate()
        except Exception as e:
            print(e)

    def check_exist_process(self, process):
        ManagerApp.logger_main.info("Check exist process")
        for p in multiprocessing.active_children():
            print(p.name)
            if p.name.__contains__(str(process)):
                return True
        return False

    def start_thread_extract_client_data(self):
        ManagerApp.logger_main.info("Start thread extract clientData from google-doc")
        p1 = Process(target=self.get_client_data_from_google_doc, name="Extract UserData thread")
        p1.start()

    def get_client_data_from_google_doc(self):
        while True:
            Control.__client_data_list = Google_Doc().get_google_doc_data()
            sleep(60)

    def get_value_client_from_clients_data(self, column_name, value_for_search):
        client_data = self.get_client_data()
        ManagerApp.logger_main.info("get_value_client_from_clients_data: client_data={}".format(client_data))
        ManagerApp.logger_main.info("Gel value client from clients list: " + "\n" +
                                    "client_data ={}".format(client_data))

        for i in client_data:
            i: dict
            v = i.values()
            print(v)
            if str(value_for_search) in str(v):
                return str(i.get(column_name))

    def get_client_from_clients_data(self, value):
        client_data = self.get_client_data()
        for client in client_data:
            for i in client.values():
                if str(i).__contains__(str(value)):
                    return client
        return None

    def get_clients_threads(self):
        process = []
        try:
            for p in multiprocessing.active_children():
                if p.name.__contains__(Control.thread):
                    print(p.name)
                    process.append(p.name)
        except Exception as e:
            print(e)

        return process

    def get_running_clients_list(self):
        number_list = set()
        clients_info_list = []

        process = self.get_clients_threads()
        print("Process: " + str(process))
        for p in process:
            value_process = p.replace(Control.thread, "")
            number_list.add(value_process)
        # for phone in number_list:
        #     client = self.get_client_from_clients_data(phone)
        #     client_info = str(client.get(Google_Doc.name)+" "+str(client.get(Google_Doc.surname)))
        #     clients_info_list.append(client_info)

        clients_list = []
        for i in number_list:
            clients_list.append(self.get_client_from_clients_data(i))
        return clients_list

    def check_date_valid(self, string, fuzzy=False):
        """
        Return whether the string can be interpreted as a date.

        :param string: str, string to check for date
        :param fuzzy: bool, ignore unknown tokens in string if True
        """
        try:
            parse(string, fuzzy=fuzzy)
            return True

        except ValueError:
            return False

    def check_email(self, email):
        EMAIL_REGEX = re.compile(r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+")
        if not EMAIL_REGEX.match(email):
            return False
        else:
            return True

    def check_valid(self, client):
        if str(client.get(Google_Doc.name)).strip() == "":
            ManagerApp.logger_main.warning("Invalid value found: {}".format(client.get(Google_Doc.name)))
            return False
        if str(client.get(Google_Doc.surname)).strip() == "":
            ManagerApp.logger_main.warning("Invalid value found: {}".format(client.get(Google_Doc.surname)))
            return False
        if len(str(client.get(Google_Doc.phone)).strip()) < 5 or str(client.get(Google_Doc.phone)).isdigit() == False:
            ManagerApp.logger_main.warning("Invalid value found: {}".format(client.get(Google_Doc.phone)))
            return False
        if self.check_email(client.get(Google_Doc.email)) == False:
            ManagerApp.logger_main.warning("Invalid value found: {}".format(client.get(Google_Doc.email)))
            return False
        if self.check_date_valid(client.get(Google_Doc.birth_date)) == False:
            ManagerApp.logger_main.warning("Invalid value found: {}".format(client.get(Google_Doc.birth_date)))
            return False
        date_order = str(client.get(Google_Doc.order_date))
        if date_order.__contains__("-") or date_order.__contains__(","):
            if date_order.__contains__(","):
                data_split = date_order.split(",")
                for i in data_split:
                    if self.check_date_valid(i.strip()) == False:
                        ManagerApp.logger_main.warning(
                            "Invalid value found: {}".format(client.get(Google_Doc.order_date)))
                        return False
            if date_order.__contains__("-"):
                data_split = date_order.split("-")
                for i in data_split:
                    if self.check_date_valid(i.strip()) == False:
                        ManagerApp.logger_main.warning(
                            "Invalid value found: {}".format(client.get(Google_Doc.order_date)))
                        return False
        return True

    def save_screen(self, driver):
        screen = "temp/succes_order/" + "".join([random.choice(string.ascii_letters) for i in xrange(10)]) + str(".png")
        driver.save_screenshot(screen)
        return screen

    def delete_temp_files(self):
        ManagerApp.logger_main.info("Delete temp directory")
        if os.path.exists("temp/"):
            shutil.rmtree(os.path.abspath("temp/"))

    def save_current_page_as_pdf(self, client):
        driver = ManagerApp().get_driver()
        phone = str(client.get(Google_Doc.phone))
        ManagerApp.logger_client.info(phone + ": Save current page as pdf")
        #ManagerApp.logger_client.info(driver.find_element_by_css_selector("#Label_Message").text)
        name_title = str(client.get(Google_Doc.name)) + "_" + str(client.get(Google_Doc.surname))
        driver.execute_script('document.title = "%s"' % name_title)
        driver.execute_script('window.print();')
        document_pdf = os.path.abspath(ManagerApp.get_value_from_config("ORDER_DOCUMENT_PATH") + name_title + ".pdf")
        ManagerApp.logger_client.info("{}: document_pdf={}".format(phone, document_pdf))
        for i in range(10):
            if os.path.exists(document_pdf):
                ManagerApp.logger_client.info("Document pdf created: {}".format(document_pdf))
                break
            else:
                sleep(3)
        if os.path.exists(document_pdf) == False:
            ManagerApp.logger_client.info("{}: Error! Document pdf don't created! {}".format(phone, document_pdf))
            return None
        return document_pdf
    def save_current_page_as_pdf2(self,client):
        driver = ManagerApp().get_driver()
        phone = str(client.get(Google_Doc.phone))
        ManagerApp.logger_client.info(phone + ": Save current page as pdf")
        #ManagerApp.logger_client.info(driver.find_element_by_css_selector("#Label_Message").text)
        name_title = str(client.get(Google_Doc.name)) + "_" + str(client.get(Google_Doc.surname))

        document_html = os.path.abspath(ManagerApp.get_value_from_config("ORDER_DOCUMENT_PATH") + name_title + ".html")
        with open(document_html, 'w') as f:
            f.write(driver.page_source)
        document_pdf = os.path.abspath(ManagerApp.get_value_from_config("ORDER_DOCUMENT_PATH") + name_title + ".pdf")
        self.execute_bash_command("google-chrome --headless --disable-gpu --print-to-pdf={} {}".format(document_pdf, document_html))
        #os.remove(document_html)
        ManagerApp.logger_client.info("{}: document_pdf={}".format(phone, document_pdf))
        for i in range(10):
            if os.path.exists(document_pdf):
                ManagerApp.logger_client.info("Document pdf created: {}".format(document_pdf))
                break
            else:
                sleep(2)
        if os.path.exists(document_pdf) == False:
            ManagerApp.logger_client.info("{}: Error! Document pdf don't created! {}".format(phone, document_pdf))
            return None
        return document_pdf



    def execute_bash_command(self, command):
        ManagerApp.logger_main.info("Execute bash-command: {}".format(command))
        try:
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            return output
        except Exception as e:
            ManagerApp.logger_main.error(e)

    def check_available_site(self):
        time_seconds_wait = 60
        while True:
            ManagerApp.logger_main.info("Checking the availability of the site {}".format(Authorization.start_page))
            try:
                if str(urllib.request.urlopen(Authorization.start_page).getcode()) == "200":
                    self.enable_monitoring()
                    break
                else:
                    ManagerApp.logger_main.warning("Website unavailable! Wait {} seconds...".format(time_seconds_wait))
                    self.disable_monitoring()
                    self.stop_all_process()
                    sleep(time_seconds_wait)
            except Exception as e:
                self.stop_all_process()
                Control.process_queue_shared = multiprocessing.Manager().list()
                ManagerApp.logger_main.warning(
                    "Website {} unavailable! Wait {} seconds...".format(Authorization.start_page, time_seconds_wait))
                self.disable_monitoring()
                sleep(time_seconds_wait)

    def create_dir_temp(self):
        ManagerApp.logger_main.info("Create temp directory")
        order = ManagerApp.get_value_from_config("ORDER_DOCUMENT_PATH")
        captcha = ManagerApp.get_value_from_config("CAPTCHA_PATH")
        if os.path.exists("temp") == False:
            os.makedirs(os.path.abspath(order))
            os.makedirs(os.path.abspath(captcha))
