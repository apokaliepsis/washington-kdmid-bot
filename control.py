import multiprocessing
import re
from time import sleep
from typing import Dict

from dateutil.parser import parse

from authorization import Authorization
from consul_services import Consul_Services
from manager_app import ManagerApp
from google_doc import Google_Doc
from multiprocessing import Pool, Process


class Control:
    __client_data_list: dict = None

    def get_client_data(self) -> dict:
        return Google_Doc().get_google_doc_data()

    def get_client_order(self, client):
        from calendar_page import Calendar_Page
        try:
            if self.check_valid(client):
                #ManagerApp().set_ip_poxy("socks5://AXWFq6:TMd7en@154.30.137.131:8000")
                ManagerApp().set_ip_poxy("socks5://70KAot:7u6J69@hub-us-6-1.litport.net:5337")
                Authorization().authorize(client)
                Consul_Services().go_to_for_get_passport()
                Calendar_Page().select_specific_slot(client)
                Calendar_Page().click_by_make_order()
                Calendar_Page().get_doc_order()
                Google_Doc().delete_row_from_doc(client.get(Google_Doc.phone))
                ManagerApp().get_driver().quit()
            else:
                ManagerApp().get_logger().warn("Incorrect client data: " + str(client))
        except:
            ManagerApp().get_logger().warn("Unexpected error. Restart client thread")
            sleep(10)
            client = self.get_client_from_clients_data(client.get(Google_Doc.phone))
            self.get_client_order(client)

    def run_main(self):
        Control.__client_data_list = Google_Doc().get_google_doc_data()
        # self.start_thread_extract_client_data()
        while True:
            if len(Control.__client_data_list) > 0:
                self.start_clients_threads(self.get_client_data())
            sleep(60)
            Control.__client_data_list = Google_Doc().get_google_doc_data()

    def start_clients_threads(self, client_data_list):
        for client in client_data_list:
            if self.check_exist_process(client.get(Google_Doc.phone)) == False:
                name_process = "ClientThread_" + str(client.get(Google_Doc.phone))
                p1 = Process(target=self.get_client_order, name=name_process, args=[client])
                p1.start()
                ManagerApp().get_logger().info("Start " + name_process)
                sleep(15)

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

    def show_clients_thread(self):
        for p in multiprocessing.active_children():
            if p.name.__contains__("ClientThread_"):
                print(p.name)

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
