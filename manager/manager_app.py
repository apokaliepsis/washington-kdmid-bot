import json
import os
import time
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import logging
import sys
import pickle
from seleniumwire import webdriver

logging.basicConfig(level=logging.ERROR)  # Main app runs at DEBUG level
logger = logging.getLogger('seleniumwire')
logger.setLevel(logging.ERROR)  # Run selenium wire at ERROR level


class ManagerApp:
    __driver: webdriver = None
    log: logging = None
    __options = None
    # driver = webdriver.Chrome(seleniumwire_options=options)
    def startDriver(self):
        chrome_options = Options()
        settings = {
            "recentDestinations": [{
                "id": "Save as PDF",
                "origin": "local",
                "account": "",
            }],
            "selectedDestinationId": "Save as PDF",
            "version": 2
        }
        path_for_save = os.path.abspath("temp/succes_order/")
        prefs = {
            'printing.print_preview_sticky_settings.appState': json.dumps(settings),
            'savefile.default_directory': path_for_save
        }
        chrome_options.add_experimental_option('prefs', prefs)
        chrome_options.add_argument('--kiosk-printing')
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")
        #chrome_options.add_argument("--headless")
        #chrome_options.add_argument("--proxy-server=http://164.155.150.1:80")
        # chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_argument("--profile-directory=Default")
        # chrome_options.add_argument("--disable-plugins-discovery")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.get_logger().info("Proxy: " + str(self.__options))
        self.__driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(),
                                         chrome_options=chrome_options, seleniumwire_options=self.__options)
        self.__driver.implicitly_wait(15)
        self.get_logger().info("session_id: "+self.__driver.session_id)
        self.get_logger().info("url: "+self.__driver.command_executor._url)
        return self.__driver
    def set_ip_poxy(self,ip):
        ManagerApp.__options = {
        'proxy': {
            #'http': 'http://64.227.14.149:80'
            'https': ip
            #'no_proxy': 'localhost,127.0.0.1'
        }

    }

    def addCookies(self):
        cookies = pickle.load(open("cookies_midpass.pkl", "rb"))
        for cookie in cookies:
            self.__driver.add_cookie(cookie)

    def get_driver(self):
        if ManagerApp.__driver is None:
            ManagerApp.__driver = self.startDriver()
        return ManagerApp.__driver

    def set_None_Driver(self):
        ManagerApp.__driver = None

    def quit_driver(self):
        self.__driver.quit()
        self.set_None_Driver()

    def get_logger(name=__file__, file='log.txt', encoding='utf-8'):
        if ManagerApp.log is None:
            ManagerApp.log = logging.getLogger(str(name))
            ManagerApp.log.setLevel(logging.DEBUG)

            formatter = logging.Formatter('[%(asctime)s] %(filename)s:%(lineno)d %(levelname)-8s %(message)s')

            fh = logging.FileHandler(file, encoding=encoding)
            fh.setFormatter(formatter)
            ManagerApp.log.addHandler(fh)

            sh = logging.StreamHandler(stream=sys.stdout)
            sh.setFormatter(formatter)
            ManagerApp.log.addHandler(sh)

        return ManagerApp.log

