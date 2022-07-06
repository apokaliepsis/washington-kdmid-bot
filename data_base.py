from manager.manager_app import ManagerApp
import sqlite3

class Data_Base:
    __connection = None
    db_path = "/home/consulWashington.db"

    @staticmethod
    def execute_select_query(query):
        print(query)
        data = []
        cursor = None
        try:
            connection = Data_Base().get_connection()
            cursor = connection.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
        except Exception as e:
            ManagerApp.logger_main.warning(e)
        finally:
            cursor.close()
        return data


    def get_connection(self):
        if Data_Base.__connection == None:
            Data_Base.__connection = sqlite3.connect(Data_Base.db_path)
            return Data_Base.__connection
        else: return Data_Base.__connection

    @staticmethod
    def execute_process(query):
        print(query)
        cursor = None
        try:
            connection = Data_Base().get_connection()
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
        except Exception as e:
            ManagerApp.logger_main.warning(e)
        finally:
            cursor.close()



    @staticmethod
    def get_data_by_query(query) -> []:
        print(query)
        connection = Data_Base().get_connection()
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
