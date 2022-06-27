import pygsheets

from manager.manager_app import ManagerApp


class Google_Doc:
    name = "Имя"
    surname = "Фамилия"
    phone = "Телефон"
    middle_name = "Отчество"
    email = "Почта"
    birth_date = "Дата рождения"
    order_date = "Дата записи"

    def get_google_doc_data(self):
        wk1 = self.get_sheet()

        client_data = wk1.get_all_records()
        print("Count clients: "+str(len(client_data)))
        for i in client_data:
            print(i)
        return client_data

    @staticmethod
    def delete_row_from_doc(value):
        try:
            wk1 = Google_Doc.get_sheet()
            client_data = wk1.get_all_records()
            count = 2
            for i in client_data:
                row = i.values()
                if str(value) in str(row):
                    print(wk1.get_row(count))
                    wk1.delete_rows(count)
                count += 1
        except Exception as e:
            ManagerApp.get_logger().info(e)

    @staticmethod
    def get_sheet():
        gc = pygsheets.authorize(
            service_account_file="settings.json")  # This will create a link to authorize
        sh = gc.open_by_url(
            "https://docs.google.com/spreadsheets/d/1qu-TfbUYCaWAmS65yya2yYKttBTTBnWpLjAF5grQtNY/edit#gid=0")
        wk1 = sh.sheet1
        return wk1

