import requests
from bs4 import BeautifulSoup

URL = 'https://www.federalreserve.gov/monetarypolicy/fomchistorical1999.htm'
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')
result = soup.find(id = 'article')
fomc_meeting = result.find_all('div', 'panel panel-default')

statement_url_list = []
for meeting in fomc_meeting:
    date = meeting.find('h5')
    for column in meeting.find_all(class_ = 'col-xs-12 col-md-6'):
        for url in column.find_all('a', href = True):
            if 'press' in url.get('href'):
                statement_url_list.append(url.get('href'))

print(statement_url_list)

for statement_url in statement_url_list:

    sub_URL = 'https://www.federalreserve.gov/' + statement_url
    sub_page = requests.get(sub_URL)
    sub_soup = BeautifulSoup(sub_page.content, 'html.parser')

    # sub_result = sub_soup.find('p')
