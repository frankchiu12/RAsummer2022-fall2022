import requests
from bs4 import BeautifulSoup, NavigableString
from nltk import tokenize
import re
from datetime import datetime

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

            if self.convert_date(date) not in date_to_text:
                date_to_text[self.convert_date(date)] = self.text

    def convert_date(self, date):
        return datetime.strptime(date, '%B %d, %Y').strftime('%m/%d/%Y')

for i in range(1999, 2022):
    webscrapper = WebScrapper(str(i))

for date, text in date_to_text.items():
    if 'Voting for the ' in text:
        tuple = text.partition('Voting for the ')
        modified_text = tuple[1] + tuple[2]
        tuple = modified_text.partition('Voting against ')

        voting_for = tuple[0].strip()
        voting_against = tuple[1] + tuple[2]

        regex = re.compile('Voting for(.*)were')
        voting_for = regex.sub('Voting for the FOMC monetary policy action were:', voting_for)
        voting_for = voting_for.replace('::', ':').replace('  ', ' ').replace(', Vice Chairman;', ';').replace(', Vice Chair;', ';').replace(', Chairman;', ';').replace(', Chair;', ';').replace(', Chair,', ';').replace(', Jr.', '').replace(', and', ';').replace(',', ';').replace('; and', ';').strip()
        voting_for = tokenize.sent_tokenize(voting_for.partition('Voting for the FOMC monetary policy action were: ')[2])[0]

        last_name_list = []
        voting_for = voting_for.split('; ')
        for name in voting_for:
            word_in_name_list = name.split(' ')
            if '' in word_in_name_list:
                word_in_name_list.remove('')
            
            last_name_list.append(word_in_name_list[len(word_in_name_list) - 1]) 

            parsed_last_name_list = []
            for last_name in last_name_list:
                parsed_last_name_list.append(last_name.strip(',.')) 
        
        number_voting_for = len(parsed_last_name_list)
        voting_for = ', '.join(parsed_last_name_list)

        voting_against = voting_against.partition(' In taking')[0].partition('In a related action, the Board of Governors ')[0].partition('1. The Open Market Desk will issue a technical note shortly after the statement providing operational details on how it will carry out these transactions.')[0]

        voting_against = tokenize.sent_tokenize(voting_against)

        voting_against_sentence_list = []
        for sentence in voting_against:
            if 'alternate' not in sentence:
                voting_against_sentence_list.append(sentence)
        voting_against = ' '.join(voting_against_sentence_list)

        if voting_against == 'Voting against the action: none.':
            voting_against = ''

        # TODO: change
        date_to_text[date] = [voting_against]

    else:
        # TODO: make into a list of 5
        date_to_text[date] = ['']

# TODO: delete
for date, text in date_to_text.copy().items():
    if date_to_text[date] == ['']:
        date_to_text.pop(date)

print(date_to_text)