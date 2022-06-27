import _thread
import glob
import multiprocessing

import signal
import sys
import threading
from http.client import RemoteDisconnected, HTTPException
import os
import random

from time import sleep

import jaydebeapi
import pdfkit
from bs4 import BeautifulSoup
from itertools import chain

from urllib3 import HTTPConnectionPool
from urllib3.exceptions import MaxRetryError, NewConnectionError

from data_base import Data_Base
from manager.control import Control
from manager.errors import Errors
from manager.manager_app import ManagerApp
from network_file.google_doc import Google_Doc

options = {
    'proxy': {
        # 'http': 'http://64.227.14.149:80'
        'https': 'socks5://AXWFq6:TMd7en@154.30.137.131:8000'
        # 'no_proxy': 'localhost,127.0.0.1'
    }
}


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
            ManagerApp.get_logger().info("Kill process")
            p.terminate()


if __name__ == '__main__':
    # ManagerApp().set_ip_poxy("socks5://LCjFKu:kVN3UD@186.65.115.27:9980")
    share_data = multiprocessing.Manager().dict()
    share_data["Active"] = "0"
    multiprocessing.Process(target=method_sdf1, name="Process_Selenium", args=(share_data,)).start()
    # Process(target=method_sdf1, name="Process_Selenium").start()
    while True:
        for p in multiprocessing.active_children():
            print(p.name)
            sleep(1)

