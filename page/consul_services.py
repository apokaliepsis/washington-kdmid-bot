from manager.manager_app import ManagerApp
from network_file.google_doc import Google_Doc


class Consul_Services:
    def go_to_for_get_passport(self, client):
        driver = ManagerApp().get_driver()
        ManagerApp.logger_client.info("{}: Choosing a passport".format(client.get(Google_Doc.phone)))

        driver.find_element_by_xpath("//*[@class='reason_enable']//*[text()='Загранпаспорт']").click()

        driver.find_element_by_css_selector("#ctl00_MainContent_CheckBoxList1_0").click()

        ManagerApp.logger_client.info("{}: Click \"Register for an appointment\"".format(client.get(Google_Doc.phone)))
        driver.find_element_by_name("ctl00$MainContent$ButtonQueue").click()