from manager.manager_app import ManagerApp
class Consul_Services:
    def go_to_for_get_passport(self):
        driver = ManagerApp().get_driver()
        ManagerApp().get_logger().info("Choosing a passport")

        driver.find_element_by_xpath("//*[@class='reason_enable']//*[text()='Загранпаспорт']").click()

        driver.find_element_by_css_selector("#ctl00_MainContent_CheckBoxList1_0").click()

        ManagerApp().get_logger().info("Click \"Register for an appointment\"")
        driver.find_element_by_name("ctl00$MainContent$ButtonQueue").click()