import pygsheets
gc = pygsheets.authorize(service_account_file="settings.json") # This will create a link to authorize
sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1qu-TfbUYCaWAmS65yya2yYKttBTTBnWpLjAF5grQtNY/edit#gid=0")

# Open worksheet

wk1 = sh.sheet1
# Or
#wk1 = sh.title # sheet1 is name of first worksheet
wk1.delete_rows(5)
docs_data = wk1.get_all_records()
for i in docs_data:
    print(i)
