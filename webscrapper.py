import requests
from bs4 import BeautifulSoup
from nltk import tokenize

year_to_text = {}
date_to_voting = {}

def WebScrapper(year):

    URL = 'https://www.federalreserve.gov/monetarypolicy/fomchistorical' + str(year) + '.htm'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    fomc_meeting = soup.find(id = 'article').find_all('div', class_ = 'panel panel-default')

    statement_url_list = []
    for meeting in fomc_meeting:
        if 'Meeting' not in meeting.find('h5').get_text():
            continue
        for column in meeting.find_all(class_ = 'col-xs-12 col-md-6'):
            for url in column.find_all('a', href = True):
                if 'press' in url.get('href'):
                    statement_url_list.append(url.get('href'))

    if year not in year_to_text:
        year_to_text[year] = []

    for statement_url in statement_url_list:

        sub_URL = 'https://www.federalreserve.gov/' + statement_url
        sub_page = requests.get(sub_URL)
        sub_soup = BeautifulSoup(sub_page.content, 'html.parser')

        date = sub_soup.find('font').get_text().replace('Release Date: ', '')

        text = ''
        for paragraph in sub_soup.find_all('p'):
            if paragraph.parent.name == 'td':
                if paragraph.find_all('p') == []:
                    text = [paragraph.get_text().replace('  ', ' ')]
                else:
                    for p in paragraph.find_all('p'):
                        if len(p) == 2 or len(p) == 1 and p.get_text() != '\n':
                            text = tokenize.sent_tokenize(p.get_text())

        if 'Last update' in text[-1]:
            del text[-1]

        if (len(text) > 1):
            text_list = []
            for sub_text in text:
                text_list.append(sub_text.strip().replace('  ', ' ').rstrip().split('\n'))
            text = ''
            for sub_text in text_list:
                text = text + ' ' + sub_text[0]
            text = text.replace('  ', '').strip()
        else:
            text_list = []
            text = text[0].split('\r\n')
            for sub_text in text:
                text_list.append(sub_text.strip())
            text = ' '.join(text_list)

        print(text)
        print('=========================================')

        year_to_text[year].append(text)

        if 'Voting for the FOMC' not in text:
            if date not in date_to_voting:
                date_to_voting[date] = []
        else:
            if date not in date_to_voting:
                date_to_voting[date] = 'yoooo'

for i in range(1999, 2002):
    webscrapper = WebScrapper(str(i))