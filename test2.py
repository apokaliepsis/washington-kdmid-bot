from time import sleep

from loguru import logger

from data_base import Data_Base
from manager.manager_app import ManagerApp

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
print(len(Data_Base.exec_query("select* from configuration where chatid=%s" % "873327794"))==0)