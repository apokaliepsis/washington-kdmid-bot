import _thread
import glob
import multiprocessing

import signal
import sys
import threading
import urllib.request
from http.client import RemoteDisconnected, HTTPException
import os
import random

from time import sleep



from loguru import logger

from manager.control import Control
from manager.errors import Errors
from manager.manager_app import ManagerApp
from network_file.google_doc import Google_Doc


def method_sdf2(data,driver):
    while True:
        #sleep(2)
        print("data=", data)
        if data["Active"] == "0":
            print("method_sdf2 working...")
            print("driver quit")
            driver.close()
            driver.quit()
            _thread.interrupt_main()


def method_sdf1(data):
    driver = ManagerApp().get_driver()

    multiprocessing.Process(target=method_sdf2, name="Controller", args=(data,driver)).start()
    try:
        driver.get("https://ya.ru")
        # print("PID=", driver.service.process.data)
        sleep(1)
        print("method_sdf1 working...")


    except Exception as e:
        print("block except")
        print(e)

    # shared_dict["method_sdf1"]=driver.service.process.pid
    # print(driver.service.process.pid)


def set_ip_proxy(ip):
    ManagerApp.__options = {
        'proxy': {
            # 'http': 'http://64.227.14.149:80'
            'https': ip
            # 'no_proxy': 'localhost,127.0.0.1'
        }
    }


def get_client_date(value):
    client_data = Control().get_client_data()

    for i in client_data:
        i: dict
        v = i.values()
        print(v)
        if value in str(v):
            return i


def func1():
    while True:
        sleep(1)
        print('Working Thread1')


def func2():
    while True:
        sleep(1)
        print('Working Thread2')


def kill_process():
    for p in multiprocessing.active_children():
        sleep(5)
        if p.name.__contains__(str("Selenium")):
            ManagerApp.logger_main.info("Kill process")
            p.terminate()
@logger.catch()
def method_1():
    return 32123/0

if __name__ == '__main__':
    #ManagerApp().set_ip_poxy("socks5://4sdBGU:E3F6K7@181.177.86.241:9526")

    #ManagerApp().set_ip_poxy("socks5://LCjFKu:kVN3UD@186.65.115.27:9980")
    client = {'Фамилия': 'Николаев', 'Имя': 'Василий', 'Отчество': '', 'Телефон': 544344, 'Почта': 'wqqqqqqq@fffff.ru', 'Дата рождения': '22.12.1904', 'Дата записи': '14.08.2022'}
    process_queue_shared = []

    #Control().get_client_order(client, process_queue_shared)
    #date_order = Control().get_value_client_from_clients_data(Google_Doc.order_date, str("544344"))
    #print(date_order)
    # ManagerApp().set_ip_poxy("socks5://weTPxd:jzzc7M@hub-us-6-1.litport.net:5935")
    ManagerApp().set_ip_poxy("socks5://4sdBGU:E3F6K7@181.177.86.241:9526")
    driver = ManagerApp().get_driver()
    driver.get("http://washington.kdmid.ru/queue/Visitor.aspx")
    driver.find_element_by_css_selector("#ctl00_MainContent_txtFam").send_keys(client.get(Google_Doc.surname))

