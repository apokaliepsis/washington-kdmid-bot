import os
import re
import sys

import requests


from time import sleep

from loguru import logger

import starter_bot
from data_base import Data_Base
from manager.control import Control
from manager.manager_app import ManagerApp
from network_file.google_doc import Google_Doc

a=("dsd",3)
b = ["sdf",323]
c = {"dsf":"sf"}
b.append(a)
b.append(c)

print(isinstance(a,tuple))
print(isinstance(b,list))
print(isinstance(c,dict))
print(a)
print(b)
print(c)

# driver = ManagerApp().get_driver()
# #ManagerApp().set_ip_poxy("http://weTPxd:jzzc7M@hub-us-6-1.litport.net:1337")
# ManagerApp().set_ip_poxy("socks5://LCjFKu:kVN3UD@186.65.115.27:9980")
# driver.get("https://whatismyipaddress.com/")
#starter_bot.send_file("client.log","873327794")
res = Control().execute_bash_command("grep MemAvailable /proc/meminfo")
mem_available = re.findall(r'\d+', str(res))[0]
print(mem_available)


