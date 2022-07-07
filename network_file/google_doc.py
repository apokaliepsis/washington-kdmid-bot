import gc
import sys

import pygsheets
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from manager.manager_app import ManagerApp


class Google_Doc:
    auth_file = sys.argv[1]
    name = "Имя"
    surname = "Фамилия"
    phone = "Телефон"
    middle_name = "Отчество"
    email = "Почта"
    birth_date = "Дата рождения"
    order_date = "Дата записи"

    def get_google_doc_data(self):
        wk1 = Google_Doc().get_sheet()
        client_data = wk1.get_all_records()
        ManagerApp.logger_main.info("Count clients: {}".format(len(client_data)))
        for i in client_data:
            print(i)
        wk1.clear()

        return client_data

    def delete_row_from_doc(self, value)-> []:
        ##value:str
        ManagerApp.logger_client.info("Delete from GoogleDoc: {}".format(value))
        try:
            sheet:pygsheets.worksheet.Worksheet = self.get_sheet()
            ManagerApp.logger_client.info("get_sheet(): {}".format(sheet))
            client_data = sheet.get_all_records()
            ManagerApp.logger_client.info("sheet.get_all_records()={}".format(client_data))
            count = 2
            for i in client_data:
                row = i.values()
                if str(value) in str(row):
                    print(sheet.get_row(count))
                    sheet.delete_rows(count)
                count += 1
        except Exception as e:
            ManagerApp.logger_client.warning(e)

    def get_sheet(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive',
                 'https://www.googleapis.com/auth/spreadsheets']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(Google_Doc.auth_file, scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open_by_url(ManagerApp.get_json_data()["document_url"]).sheet1
        return worksheet

    def delete_row_gspread(self, value):
        ManagerApp.logger_client.info("Delete from GoogleDoc: {}".format(value))
        worksheet = self.get_sheet()
        client_data = worksheet.get_all_records()
        count = 2
        for i in client_data:
            row = i.values()
            if str(value) in str(row):
                worksheet.delete_rows(count)
                break
            count += 1

    def get_googledoc_data_gspread(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive',
                 'https://www.googleapis.com/auth/spreadsheets']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(Google_Doc.auth_file, scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open_by_url(ManagerApp.get_json_data()["document_url"]).sheet1
        client_data = worksheet.get_all_records()
        return client_data

