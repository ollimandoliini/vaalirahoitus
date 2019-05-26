from bs4 import BeautifulSoup
import requests
import json
import gzip
import pprint
import pandas as pd

df = pd.read_excel('election_funding.xlsx')

print(df.head())
