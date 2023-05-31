import requests
from bs4 import BeautifulSoup

milling_html = requests.get('https://www.wow-professions.com/guides/milling-table-inscription')
text = BeautifulSoup(milling_html.text, 'html.parser')

for tag in text.find_all('td'):
    print(tag.a)

