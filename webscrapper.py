import requests
from bs4 import BeautifulSoup, NavigableString
from nltk import tokenize
import re

date_to_text = {}
date_to_voting = {}

class WebScrapper():

    def __init__(self, year): 

        if int(year) < 2017:
            self.URL = 'https://www.federalreserve.gov/monetarypolicy/fomchistorical' + year + '.htm'
        else:
            self.URL = 'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm'

        self.page = requests.get(self.URL)
        self.soup = BeautifulSoup(self.page.content, 'html.parser')
        self.statement_url_list = []
        self.text = ''

        if int(year) <= 2017:
            self.populate_statement_url_list(year)
            self.get_text(year)

    def populate_statement_url_list(self, year):
        if int(year) < 2011:
            for meeting in self.soup.find(id = 'article').find_all(class_ = 'panel panel-default'):
                if 'Meeting' not in meeting.find('h5').get_text():
                    continue
                for column in meeting.find_all(class_ = 'col-xs-12 col-md-6'):
                    for url in column.find_all('a', href = True):
                        if 'press' in url.get('href'):
                            self.statement_url_list.append(url.get('href'))
        elif 2011 <= int(year) < 2017:
            for meeting in self.soup.find(id = 'article').find_all(class_ = 'panel panel-default panel-padded'):
                if 'Meeting' not in meeting.find('h5').get_text():
                    continue
                for column in meeting.find_all(class_ = 'col-xs-12 col-md-6'):
                    for url in column.find_all('a', href = True):
                        if 'press' in url.get('href'):
                            self.statement_url_list.append(url.get('href'))
        else:
            for meeting_year in self.soup.find(id = 'article').find_all(class_ = 'panel panel-default'):
                for meeting in meeting_year:
                    if isinstance(meeting, NavigableString):
                        continue
                    if meeting.get('class') == 'panel-heading' or meeting.get('class') == 'panel-footer':
                        continue
                    if '(notation value)' in meeting.get_text() or '(unscheduled)' in meeting.get_text():
                        continue
                    for url in meeting.find_all('a', href = True):
                        if 'press' in url.get('href') and url.get_text() == 'HTML':
                            self.statement_url_list.append(url.get('href'))
                            break

    def get_text(self, year):
        for statement_url in self.statement_url_list:
            if int(year) < 2006:
                self.sub_URL = 'https://www.federalreserve.gov/' + statement_url
                self.sub_page = requests.get(self.sub_URL)
                self.sub_soup = BeautifulSoup(self.sub_page.content, 'html.parser')
                date = self.sub_soup.find('font').get_text().replace('Release Date: ', '')

                for td in self.sub_soup.find_all('td'):
                    self.text = tokenize.sent_tokenize(td.get_text())
            else: 
                self.sub_URL = 'https://www.federalreserve.gov/' + statement_url
                self.sub_page = requests.get(self.sub_URL)
                self.sub_soup = BeautifulSoup(self.sub_page.content, 'html.parser')
                date = self.sub_soup.find(class_ = 'article__time').get_text().replace('Release Date: ', '')

                for article in self.sub_soup.find_all(class_ = 'col-xs-12 col-sm-8 col-md-8'):
                    self.text = tokenize.sent_tokenize(article.get_text())

            if 'Last update: ' in self.text[-1]:
                del self.text[-1]

            text_list = []
            regex = re.compile(r'[\n\r\t]')
            for sub_text in self.text:
                text_list.append(re.sub(' +', ' ', regex.sub(' ', sub_text).strip()))

            self.text = ''
            for sub_text in text_list:
                self.text = self.text + ' ' + sub_text
            self.text = self.text.replace(u'\xa0', u' ').strip()

            if 'For immediate release' in self.text:
                self.text = self.text.partition('For immediate release ')[2]

            self.text = tokenize.sent_tokenize(self.text)
            if self.text[-1][-1] != '.':
                del self.text[-1]
            self.text = ' '.join(self.text)

            if date not in date_to_text:
                date_to_text[date] = self.text

for i in range(1999, 2022):
    webscrapper = WebScrapper(str(i))

for date, text in date_to_text.items():
    if date == 'March 19, 2002':
        print('reaching')
        print(text)
        print('Voting for the ' in text)
    if 'Voting for the ' in text:
        tuple = text.partition('Voting for the ')
        modified_text = tuple[1] + tuple[2]
        tuple = modified_text.partition('Voting against ')
        date_to_text[date] = [tuple[0].strip(), tuple[1] + tuple[2]]
    else:
        date_to_text[date] = ['', '', '', '', '']

print(date_to_text)