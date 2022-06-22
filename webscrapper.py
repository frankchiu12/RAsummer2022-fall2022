import requests
from bs4 import BeautifulSoup
from nltk import tokenize
import re

date_to_voting = {}

class WebScrapper():

    def __init__(self, year): 

        self.URL = 'https://www.federalreserve.gov/monetarypolicy/fomchistorical' + year + '.htm'
        self.page = requests.get(self.URL)
        self.soup = BeautifulSoup(self.page.content, 'html.parser')
        self.statement_url_list = []
        self.text = ''

        self.populate_statement_url_list()
        self.get_text(year)

    def populate_statement_url_list(self):     
        for meeting in self.soup.find(id = 'article').find_all('div', class_ = 'panel panel-default'):
            if 'Meeting' not in meeting.find('h5').get_text():
                continue
            for column in meeting.find_all(class_ = 'col-xs-12 col-md-6'):
                for url in column.find_all('a', href = True):
                    if 'press' in url.get('href'):
                        self.statement_url_list.append(url.get('href'))

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
            self.text = self.text.strip()

            if 'For immediate release' in self.text:
                self.text = self.text.partition('For immediate release ')[2]

            print(date)
            print(self.text)
            print('\n')

    def parse_text(self):
        pass

for i in range(1999, 2017):
    webscrapper = WebScrapper(str(i))