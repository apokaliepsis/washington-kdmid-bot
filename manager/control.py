import _thread
import glob
import multiprocessing
import subprocess
import sys
from multiprocessing import Process
import os
import random
import re
import string
from time import sleep
from cffi.backend_ctypes import xrange
from dateutil.parser import parse

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

    def get_client_data(self) -> dict:
        return Google_Doc().get_google_doc_data()

    def control_activity_process(self, process_queue_shared, client, driver):
        name = str(client.get(Google_Doc.name) + " " + client.get(Google_Doc.surname))
        phone = client.get(Google_Doc.phone)

        try:
            while True:
                print("Control_Process: queue=", process_queue_shared)
                for client_process in process_queue_shared:
                    client_process_phone = client_process.get("PHONE")
                    print("PRONE=", client_process_phone)
                    if client_process_phone == phone and client_process.get("ACTIVE") == 0:
                        ManagerApp.get_logger().info("Close process for " + name)
                        # driver.close()
                        # Google_Doc.delete_row_from_doc(phone)
                        Data_Base.exec_query("delete from sessions where phone='%s'" % phone)
                        driver.quit()
                        ManagerApp.get_logger().info("Quit driver for " + name)
                        # process_queue.remove(client_process)
                        #Control.execute_bash_command()
                        _thread.interrupt_main()
                sleep(5)
        except Exception as e:
            ManagerApp.get_logger().info(e)

    def get_client_order(self, client, process_queue_shared):
        from page.calendar_page import Calendar_Page
        try:
            if self.check_valid(client):
                driver = ManagerApp().get_driver()
                self.add_sessions(client)
                #if process_queue.__contains__()
                pid = driver.service.process.pid
                print("PID=",pid)
                for item in process_queue_shared:
                    if client.get(Google_Doc.phone) in item.values():
                        process_queue_shared.remove(item)
                process_queue_shared.append({"PHONE": client.get(Google_Doc.phone), "ACTIVE": 1, "PID":pid})

                control_activity_process = Process(
                    target=Control().control_activity_process,
                    name="Control_Process_" + str(client.get(Google_Doc.phone)), args=(process_queue_shared, client, driver))
                control_activity_process.start()

                ManagerApp().set_ip_poxy("socks5://4sdBGU:E3F6K7@181.177.86.241:9526")
                # ManagerApp().set_ip_poxy("socks5://70KAot:7u6J69@hub-us-6-1.litport.net:5337")
                # ManagerApp().set_ip_poxy("socks5://LCjFKu:kVN3UD@186.65.115.27:9980")

                Authorization().authorize(client)
                Consul_Services().go_to_for_get_passport()
                Calendar_Page().select_specific_slot(client)
                Calendar_Page().click_by_make_order()
                driver.implicitly_wait(600)
                Calendar_Page().click_by_print()
                self.save_current_page_as_pdf(client)
                driver.implicitly_wait(15)
                Google_Doc().delete_row_from_doc(client.get(Google_Doc.phone))
                ManagerApp().quit_driver()

                # sleep(600)
                self.delete_client_from_sessions(client)
                control_activity_process.terminate()
                sys.exit()
            else:
                ManagerApp().get_logger().warn("Incorrect client data: " + str(client))
        except:
            ManagerApp().get_logger().warn("Unexpected error. Restart client thread")
            ManagerApp().quit_driver()
            client = self.get_client_from_clients_data(client.get(Google_Doc.phone))
            self.get_client_order(client, process_queue_shared)

    def delete_client_from_sessions(self, client):
        ManagerApp().get_logger().info("Delete from sessions client: " + str(client))
        fio = str(client.get(Google_Doc.name)) + " " + str(client.get(Google_Doc.surname))
        Data_Base.exec_query("delete from sessions where fio='%s'" % fio)

    def run_main(self):

        bot_process = Process(target=start_bot, name="Bot", args=(Control.process_queue_shared,))
        bot_process.start()

        # session_control = Process(
        #     target=self.control_sessions_queue,
        #     name="Session_Conctrol",
        #     args=(Control.process_queue_shared,))
        # session_control.start()
        self.delete_temp_files_from()
        #self.delete_sessions()
        Control.__client_data_list = Google_Doc().get_google_doc_data()
        # self.start_thread_extract_client_data()
        while True:
            if Control.__client_data_list is not None and len(Control.__client_data_list) > 0:
                self.start_clients_threads(self.get_client_data())
            Control.__client_data_list = Google_Doc().get_google_doc_data()
            self.control_sessions_queue()
            sleep(5)

    def control_sessions_queue(self):
        try:
            print("control_sessions: process_queue_shared before=", Control.process_queue_shared)
            for client in Control.process_queue_shared:
                print("control_sessions: client=", client)
                if client["ACTIVE"] == 0:
                    phone = str(client.get("PHONE"))
                    print("control_sessions_db: ", phone)
                    for p in multiprocessing.active_children():
                        if p.name.__contains__(Control.thread) and p.name.__contains__(phone):
                            ManagerApp.get_logger().info("Session_Conctrol: Process " + str(p.name) + " terminate")
                            p.kill()
                            Control.process_queue_shared.remove(client)
            print("control_sessions : process_queue_shared after=", Control.process_queue_shared)
            # sleep(5)

        except Exception as e:
            ManagerApp.get_logger().warn(str(e))

    def delete_sessions(self):
        ManagerApp.get_logger().info("Delete sessions")
        Data_Base.exec_query("delete from sessions")
        print("select* from sessions=",Data_Base.exec_query("select* from sessions"))

    def start_clients_threads(self, client_data_list):
        for client in client_data_list:
            if self.check_exist_process(client.get(Google_Doc.phone)) == False:
                name_process = "ClientThread_" + str(client.get(Google_Doc.phone))
                p1 = Process(target=self.get_client_order, name=name_process,
                             args=(client, Control.process_queue_shared))
                p1.start()
                ManagerApp().get_logger().info("Start " + name_process)
            sleep(5)

    def add_sessions(self, client):
        fio = str(client.get(Google_Doc.name) + " " + client.get(Google_Doc.surname))
        order_date = client.get(Google_Doc.order_date)
        phone = client.get(Google_Doc.phone)
        active = 1
        if len(Data_Base.get_data_by_query("select* from sessions where phone='%s'" % phone))>0:
            Data_Base.exec_query("delete from sessions where phone='%s'" % phone)
        Data_Base.exec_query(
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
        for p in multiprocessing.active_children():
            print(p.name)
            if p.name.__contains__(str(process)):
                return True

        return False

    def start_thread_extract_client_data(self):
        ManagerApp().get_logger().info("Start thread extract clientData from google-doc")
        p1 = Process(target=self.get_client_data_from_google_doc, name="Extract UserData thread")
        p1.start()

    def get_client_data_from_google_doc(self):
        while True:
            Control.__client_data_list = Google_Doc().get_google_doc_data()
            sleep(60)

    def get_value_client_from_clients_data(self, column_name, value_for_search):
        client_data = self.get_client_data()
        for i in client_data:
            i: dict
            v = i.values()
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

    # def check_running_clients_with_db(self):
    #     clients_running_list = self.get_running_clients_list()
    #     for client in clients_running_list:
    #         fio = str(client.get(Google_Doc.name)+" "+str(client.get(Google_Doc.surname)))
    #         if len(Data_Base.get_data_by_query("select * from sessions where fio='%s'" % fio)) == 0:
    #             self.add_sessions(client)
    # client_session_list = Data_Base.get_data_by_query("select * from sessions")
    # for client in client_session_list:
    #     exist_list = []
    #     fio = client.get("FIO")
    #     for client_thread in clients_running_list:
    #         client_thread: dict
    #         if client_thread.__contains__(str(fio).split()[1]):
    #             exist_list.append(True)
    #         else:
    #             exist_list.append(False)
    #     if exist_list.__contains__(False):
    #         Data_Base.exec_query("delete from sessions where fio='%s'" % fio)

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
            ManagerApp().get_logger().warn("Invalid value found: " + str(client.get(Google_Doc.name)))
            return False
        if str(client.get(Google_Doc.surname)).strip() == "":
            ManagerApp().get_logger().warn("Invalid value found: " + str(client.get(Google_Doc.surname)))
            return False
        if len(str(client.get(Google_Doc.phone)).strip()) < 5 or str(client.get(Google_Doc.phone)).isdigit() == False:
            ManagerApp().get_logger().warn("Invalid value found: " + str(client.get(Google_Doc.phone)))
            return False
        if self.check_email(client.get(Google_Doc.email)) == False:
            ManagerApp().get_logger().warn("Invalid value found: " + str(client.get(Google_Doc.email)))
            return False
        if self.check_date_valid(client.get(Google_Doc.birth_date)) == False:
            ManagerApp().get_logger().warn("Invalid value found: " + str(client.get(Google_Doc.birth_date)))
            return False
        date_order = str(client.get(Google_Doc.order_date))
        if date_order.__contains__("-") or date_order.__contains__(","):
            if date_order.__contains__(","):
                data_split = date_order.split(",")
                for i in data_split:
                    if self.check_date_valid(i.strip()) == False:
                        ManagerApp().get_logger().warn("Invalid value found: " + str(client.get(Google_Doc.order_date)))
                        return False
            if date_order.__contains__("-"):
                data_split = date_order.split("-")
                for i in data_split:
                    if self.check_date_valid(i.strip()) == False:
                        ManagerApp().get_logger().warn("Invalid value found: " + str(client.get(Google_Doc.order_date)))
                        return False
        return True

    def save_screen(self, driver):
        screen = "temp/succes_order/" + "".join([random.choice(string.ascii_letters) for i in xrange(10)]) + str(".png")
        driver.save_screenshot(screen)
        return screen

    def delete_temp_files_from(self):
        folders = ["temp/captcha_img/*", "temp/succes_order/*"]
        ManagerApp().get_logger().info("Deleting temporary files: " + str(folders))
        for folder in folders:
            files = glob.glob(folder)
            for f in files:
                os.remove(f)

    def save_current_page_as_pdf(self, client):
        driver = ManagerApp().get_driver()
        ManagerApp.get_logger().info(driver.find_element_by_css_selector("#Label_Message").text)
        name_title = str(client.get(Google_Doc.name)) + "_" + str(client.get(Google_Doc.surname))
        driver.execute_script('document.title = "%s"' % name_title)
        driver.execute_script('window.print();')

    def execute_bash_command(self, command):
        try:
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            return output
        except Exception as e:
            ManagerApp.get_logger().error(e)
            ManagerApp.get_logger().error(e)
