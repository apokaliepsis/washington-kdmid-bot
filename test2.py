from control import Control
from google_doc import Google_Doc
from manager_app import ManagerApp

# client = Google_Doc().get_google_doc_data()[0]
# print(Control().check_valid(client))
date_order="24.07.2022, 21.08.2022"
if str(date_order).__contains__("-") or str(date_order).__contains__(","):
    print(True)
else: print(False)