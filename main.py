from authorization import Authorization
from consul_services import Consul_Services
from calendar_page import Calendar_Page
from threading import Thread
from control import Control
from time import sleep
from multiprocessing import Pool, Process
from google_doc import Google_Doc


if __name__ == '__main__':
    #Control().get_user_order()
    # thread1 = Thread(target=Control().get_user_order)
    # thread2 = Thread(target=Control().get_user_order)
    # thread1.start()
    # thread2.start()
    # p1 = Process(target=Control().get_user_order)
    # p1.start()

    #Control().get_user_order(Google_Doc().get_google_doc_data()[0])

    Control().run_main()
    # p2 = Process(target=Control().get_user_order)
    # p2.start()

