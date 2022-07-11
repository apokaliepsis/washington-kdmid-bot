import _thread
import glob
import multiprocessing

import signal
import sqlite3
import sys
import threading
import urllib.request
from http.client import RemoteDisconnected, HTTPException
import os
import random
from multiprocessing import Process

from time import sleep

import jaydebeapi
import requests
from loguru import logger
from memory_profiler import profile

from data_base import Data_Base
from db_sqlite import DB_Sqlite
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

@profile
def method_1():
    client_data = None
    for i in range(15):
        client_data = Google_Doc().get_google_doc_data()
        print(client_data)


if __name__ == '__main__':
    client = {'Фамилия': 'Николаев', 'Имя': 'Василий', 'Отчество': '', 'Телефон': 544344, 'Почта': 'wqqqqqqq@fffff.ru', 'Дата рождения': '22.12.1904', 'Дата записи': '14.08.2022'}
    process_queue_shared = []
    # Control().get_client_order(client, process_queue_shared)
    #date_order = Control().get_value_client_from_clients_data(Google_Doc.order_date, str("544344"))
    #print(date_order)

    # ManagerApp().set_ip_poxy(ManagerApp.get_json_data()["proxy_url"])
    # driver = ManagerApp().get_driver()
    # #driver.get("https://2ip.ru")
    #
    # for i in range(0,1,30):
    #     ManagerApp.logger_main.info("Rotate proxy")
    #     requests.get("https://litport.net/sys/pool-select?key=3fc9349fadb9a2f8018b775b6154be1f&num=%s" % i)
    #     driver.get("https://2ip.ru")
    #     sleep(30)











