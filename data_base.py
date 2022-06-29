import jaydebeapi
from manager.manager_app import ManagerApp


class Data_Base:
    @staticmethod
    def exec_query(query):
        print(query)
        connection = jaydebeapi.connect(
            "org.h2.Driver",
            "jdbc:h2:tcp://localhost/~/consulWashingtonH2",
            ["admin", "123456"],
            "h2-2.0.202.jar")
        cursor = connection.cursor()
        data = []
        try:
            cursor.execute(query)
            data = cursor.fetchall()
            print(data)

        except Exception as e:
            print("Data_Base except: ",e)
            ManagerApp.logger_main.warning(e)
        finally:
            cursor.close()
            connection.close()
        return data


    @staticmethod
    def get_cursor():
        connection = jaydebeapi.connect(
            "org.h2.Driver",
            "jdbc:h2:tcp://localhost/~/consulWashingtonH2",
            ["admin", "123456"],
            "h2-2.0.202.jar")
        cursor = connection.cursor()
        return connection, cursor

    @staticmethod
    def get_data_by_query(query) -> []:
        connection, cursor = Data_Base.get_cursor()
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
            connection.close()
        return result
    def exec_query2(query):
        print(query)
        db_username = ManagerApp.get_value_from_config("DB_USERNAME")
        db_password = ManagerApp.get_value_from_config("DB_PASSWORD")
        db_host = ManagerApp.get_value_from_config("DB_HOST")
        connection = jaydebeapi.connect(
            "org.h2.Driver",
            db_host,
            [db_username, db_password],
            "h2-2.0.202.jar")
        cursor = connection.cursor()
        data = []
        try:
            cursor.execute(query)
            data = cursor.fetchall()
            print(data)
            cursor.close()
            connection.close()
        except Exception as e:
            print("Data_Base except: ",e)
            ManagerApp.logger_main.warning(e)
        return data