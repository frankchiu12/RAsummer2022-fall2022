import requests
from bs4 import BeautifulSoup, NavigableString
import re
from datetime import datetime
from pathlib import Path

date_to_text = {}

class Automated_Saver():

    def __init__(self, year):

        if int(year) < 2017:
            URL = 'https://www.federalreserve.gov/monetarypolicy/fomchistorical' + year + '.htm'
        else:
            URL = 'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm'
        page = requests.get(URL)
        self.soup = BeautifulSoup(page.content, 'html.parser')
        self.statement_url_list = []
        self.text = ''

        if int(year) <= 2017:
            self.get_statement_url(year)
            self.get_text(year)

    def get_statement_url(self, year):
        if int(year) < 2011:
            self.get_statement_url_helper('panel panel-default')
        elif 2011 <= int(year) < 2017:
            self.get_statement_url_helper('panel panel-default panel-padded')
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

    def get_statement_url_helper(self, HTML_class):
        for meeting in self.soup.find(id = 'article').find_all(class_ = HTML_class):
            if 'Meeting' not in meeting.find('h5').get_text():
                continue
            for column in meeting.find_all(class_ = 'col-xs-12 col-md-6'):
                for url in column.find_all('a', href = True):
                    if 'press' in url.get('href'):
                        self.statement_url_list.append(url.get('href'))

    def get_text(self, year):
        for statement_url in self.statement_url_list:
            sub_URL = 'https://www.federalreserve.gov/' + statement_url
            sub_page = requests.get(sub_URL)
            sub_soup = BeautifulSoup(sub_page.content, 'html.parser')
            if int(year) < 2006:
                date = sub_soup.find('font').get_text().replace('Release Date: ', '')
                for article in sub_soup.find_all('td'):
                    self.text = re.compile(r'[\n\r\t]').sub(' ', article.get_text().replace(u'\xa0', u' ')).strip()
            else: 
                date = sub_soup.find(class_ = 'article__time').get_text().replace('Release Date: ', '')
                for article in sub_soup.find_all(class_ = 'col-xs-12 col-sm-8 col-md-8'):
                    self.text = re.compile(r'[\n\r\t]').sub(' ', article.get_text().replace(u'\xa0', u' ')).strip()

            if self.convert_date(date) not in date_to_text:
                if self.convert_date(date) == '03/23/2020':
                    continue
                else:
                    date_to_text[self.convert_date(date)] = self.text

    def convert_date(self, date):
        try:
            return datetime.strptime(date, '%B %d, %Y').strftime('%Y%m%d')
        except ValueError:
            return datetime.strptime(date, '%b %d, %Y').strftime('%Y%m%d')

for year in range(2017, 2023):
    webscrapper = Automated_Saver(str(year))

dir_path = Path('/Users/franksi-unchiu/Desktop/Handlan Summer Research 2022')

for date, text in date_to_text.items():
    file_name = 'Astatement' + date + '.txt'
    with open (dir_path.joinpath(file_name), 'w') as f:
        f.write(text)

for file in dir_path.iterdir():
    if file.is_file() and file.stem != '.DS_Store':
        directory = file.parent
        extension = file.suffix
        name = file.stem
        name_year = file.stem[10:14]
        name_extension = name + extension
        new_path = dir_path.joinpath(name_year)

        if not new_path.exists():
            new_path.mkdir()

        new_file_path = new_path.joinpath(name_extension)
        file.replace(new_file_path)