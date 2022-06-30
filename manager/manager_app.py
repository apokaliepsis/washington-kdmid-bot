import json
import os
from configobj import ConfigObj
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import logging
from loguru import logger
import sys
import pickle
from seleniumwire import webdriver

selenium_logger = logging.getLogger('seleniumwire')
selenium_logger.setLevel(logging.ERROR)
# easyocr_logger = logging.getLogger('easyocr')
# easyocr_logger.setLevel(logging.ERROR)

logger.add("main.log", filter=lambda record: record["extra"].get("name") == "logger_main", format="{time:YYYY-MM-DD HH:mm:ss.SSS} {name} {message}", level="DEBUG", rotation="1 MB")
logger.add("client.log", filter=lambda record: record["extra"].get("name") == "logger_client", format="{time:YYYY-MM-DD HH:mm:ss.SSS} {name} {message}", level="DEBUG", rotation="1 MB")
class ManagerApp:
    logger_main = logger.bind(name="logger_main")
    logger_client = logger.bind(name="logger_client")
    __driver: webdriver = None
    __log_seleniumwire: logging = None
    __options = None
    __path_settings_file: str = sys.argv[1]
    __json_data: json = None

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
        path_for_order_document = self.get_value_from_config("ORDER_DOCUMENT_PATH")
        path_for_save = os.path.abspath(path_for_order_document)
        prefs = {
            'printing.print_preview_sticky_settings.appState': json.dumps(settings),
            'savefile.default_directory': path_for_save
        }
        chrome_options.add_experimental_option('prefs', prefs)
        chrome_options.add_argument('--kiosk-printing')
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")
        # chrome_options.add_argument("--headless")
        #chrome_options.add_argument("--proxy-server=socks5://4sdBGU:E3F6K7@181.177.86.241:9526")
        # chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_argument("--profile-directory=Default")
        # chrome_options.add_argument("--disable-plugins-discovery")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        ManagerApp.logger_main.info("Proxy: " + str(self.__options))
        self.__driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(),
                                         chrome_options=chrome_options, seleniumwire_options=self.__options)
        self.__driver.implicitly_wait(15)
        ManagerApp.logger_main.info("session_id: " + self.__driver.session_id)
        return self.__driver

    def set_ip_poxy(self, ip):
        ManagerApp.logger_main.info("Set proxy...")
        ManagerApp.__options = {
            'proxy': {
                # 'http': 'http://64.227.14.149:80'
                'https': ip
                # 'no_proxy': 'localhost,127.0.0.1'
            }
        }
        ManagerApp.logger_main.info("Proxy: "+str(ManagerApp.__options))

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

    @staticmethod
    def get_logger():
        if ManagerApp.logger is None:
            ManagerApp.logger = logger
            ManagerApp.logger.add("main.log", format="{time:YYYY-MM-DD HH:mm:ss.SSS} {name} {message}",
                                  level="DEBUG", rotation="1 MB")
            # ManagerApp.log.setLevel(logging.DEBUG)
            # formatter = logging.Formatter('[%(asctime)s] %(filename)s:%(lineno)d %(levelname)-8s %(message)s')
            # fh = logging.FileHandler(file, encoding=encoding)
            # fh.setFormatter(formatter)
            # ManagerApp.log.addHandler(fh)
            # sh = logging.StreamHandler(stream=sys.stdout)
            # sh.setFormatter(formatter)
            # ManagerApp.log.addHandler(sh)
        return ManagerApp.logger

    def get_json_data(self):
        if ManagerApp.__json_data is None:
            with open(ManagerApp.__path_settings_file) as f:
                ManagerApp.__json_data = json.load(f)
        return ManagerApp.__json_data
    @staticmethod
    def get_value_from_config(value):
        conf = ConfigObj("settings.env")
        return conf[value]