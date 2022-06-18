import logging
import multiprocessing
import random
import re
import sys
from concurrent import futures
from dateutil.parser import parse
import pygsheets
import requests
from multiprocessing import Pool, Process
from multiprocessing.pool import ThreadPool
from threading import Thread
from time import sleep

from control import Control
from manager_app import ManagerApp
from fp.fp import FreeProxy
from joblib import Parallel, delayed
from google_doc import Google_Doc
import threading
from calendar_page import Calendar_Page

# def func1():
#     while True:
#         sleep(1)
#         print('Working Thread1')
#
# def func2():
#     while True:
#         sleep(1)
#         print('Working Thread2')

options = {
    'proxy': {
        # 'http': 'http://64.227.14.149:80'
        'https': 'socks5://AXWFq6:TMd7en@154.30.137.131:8000'
        # 'no_proxy': 'localhost,127.0.0.1'
    }
}
def method_sdf1():

    # driver = ManagerApp().get_driver()
    # driver.get("https://2ip.ru")
    while True:
        print("Working...")
        sleep(3)

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
        i:dict
        v = i.values()
        print(v)
        if value in str(v):
            return i



if __name__ == '__main__':
    # ManagerApp().set_ip_poxy("socks5://AXWFq6:TMd7en@154.30.137.131:8000")
    # method_sdf1()
    ManagerApp().set_ip_poxy("socks5://70KAot:7u6J69@hub-us-6-1.litport.net:5337")

    ManagerApp().get_driver().get("https://2ip.ru")
    # p1 = Process(target=method_sdf1, name="поток1")
    # p1.start()
    # p2 = Process(target=method_sdf1, name="поток"+str(random.randint(0,100)))
    # p2.start()






