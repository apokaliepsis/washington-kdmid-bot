import requests
import pandas as pd
from fp.fp import FreeProxy

proxy = FreeProxy(country_id=['US']).get()
print(proxy)