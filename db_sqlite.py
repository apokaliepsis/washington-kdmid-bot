import sqlite3
from manager.manager_app import ManagerApp


class DB_Sqlite:
    __connection = None

    @staticmethod
    def execute_select_query(query):
        print(query)
        db_path = "/home/anton/consulWashington.db"
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        connection.close()
        cursor.close()
        return data
    @staticmethod
    def execute_process(query):
        print(query)
        db_path = "/home/anton/consulWashington.db"
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(query)
        connection.close()
        cursor.close()

    @staticmethod
    def get_data_by_query(query) -> []:
        print(query)
        db_path = "/home/anton/consulWashington.db"
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        result = []
        try:
            cursor.execute(query)
            column_name_data = cursor.description
            column_name = []
            for v in column_name_data:
                column_name.append(v[0])
            data = cursor.fetchall()
            for row in data:
                row_result = {}
                index = 0
                for cell in row:
                    #row_result.append({column_name[index]: str(cell).strip()})
                    row_result[column_name[index]] = str(cell).strip()
                    index += 1
                result.append(row_result)
        except Exception as e:
            ManagerApp.logger_main.warning(e)
        finally:
            cursor.close()

        return result
