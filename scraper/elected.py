import json
from bs4 import BeautifulSoup
import requests

url = 'https://fi.wikipedia.org/wiki/Luettelo_vaalikauden_2019%E2%80%932023_kansanedustajista'
html = requests.get(url).content
soup = BeautifulSoup(html, features="html.parser")
table = soup.find_all('table')[3].find('tbody').find_all('span')


def format_name(name):
    split = name.split(' ')
    reverse = list(reversed(split))
    return ', '.join(reverse)


elected = [row.find('span').text for row in table if row.find('span')]

formatted = list(map(format_name, elected))

with open('elected.json', 'w') as file:
    json.dump(formatted, file)
