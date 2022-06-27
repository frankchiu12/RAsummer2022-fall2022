import requests
from bs4 import BeautifulSoup, NavigableString
import re
from nltk import tokenize
from datetime import datetime
import spacy
nlp = spacy.load('en_core_web_md')
import pygsheets
from pygsheets.datarange import DataRange

sheet = pygsheets.authorize(service_account_file = 'write_into_google_sheet.json').open('Summer RA')
date_to_minute = {}
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
            self.get_release_information(year)
            self.populate_statement_url_list(year)
            self.get_text(year)

    def get_release_information(self, year):
        if int(year) < 2011:
            for meeting in self.soup.find(id = 'article').find_all(class_ = 'panel panel-default'):
                if 'Meeting' not in meeting.find('h5').get_text():
                    continue
                if 'Statement' not in meeting.get_text():
                    continue

                date = meeting.find('h5').get_text().partition('Meeting - ')
                date = ''.join(date[0] + date[2])
                date = date.split(' ')
                date_word_list = []
                date[1] = date[1] + ','
                for word in date:
                    if '-' in word:
                        word = word.split('-')[1]
                    date_word_list.append(word)
                date = self.convert_date(' '.join(date_word_list))

                for column in meeting.find_all(class_ = 'col-xs-12 col-md-6'):
                    for p in column.find_all('p'):
                        for a in p.find_all('a', href = True):
                            if 'minutes' in a.get('href'):
                                if date not in date_to_minute:
                                    if re.findall('Released (.*?)\)', p.get_text()) != []:
                                        date_to_minute[date] = self.convert_date(re.findall('Released (.*?)\)', p.get_text())[0])
        elif 2011 <= int(year) < 2017:
            for meeting in self.soup.find(id = 'article').find_all(class_ = 'panel panel-default panel-padded'):
                if 'Meeting' not in meeting.find('h5').get_text():
                    continue
                if 'Statement' not in meeting.get_text():
                    continue

                date = meeting.find('h5').get_text().partition('Meeting - ')
                date = ''.join(date[0] + date[2])
                date = date.split(' ')
                date_word_list = []
                if len(date) == 5:
                    date_word_list.append(date[1].partition('-')[2] + ' ' + date[2] + ',')
                    date_word_list.append(date[4])
                else:
                    date[1] = date[1] + ','
                    for word in date:
                        if '/' in word:
                            word = word.split('/')[1]
                        if '-' in word:
                            word = word.split('-')[1]
                        date_word_list.append(word)
                date = self.convert_date(' '.join(date_word_list))

                for column in meeting.find_all(class_ = 'col-xs-12 col-md-6'):
                    for p in column.find_all('p'):
                        for a in p.find_all('a', href = True):
                            if 'minutes' in a.get('href'):
                                if date not in date_to_minute:
                                    if re.findall('Released (.*?)\)', p.get_text()) != []:
                                        date_to_minute[date] = self.convert_date(re.findall('Released (.*?)\)', p.get_text())[0])

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

    def get_text(self, year):
        for statement_url in self.statement_url_list:
            if int(year) < 2006:
                self.sub_URL = 'https://www.federalreserve.gov/' + statement_url
                self.sub_page = requests.get(self.sub_URL)
                self.sub_soup = BeautifulSoup(self.sub_page.content, 'html.parser')
                date = self.sub_soup.find('font').get_text().replace('Release Date: ', '')
                # split into list ofsentences
                for td in self.sub_soup.find_all('td'):
                    self.text = tokenize.sent_tokenize(td.get_text())
            else: 
                self.sub_URL = 'https://www.federalreserve.gov/' + statement_url
                self.sub_page = requests.get(self.sub_URL)
                self.sub_soup = BeautifulSoup(self.sub_page.content, 'html.parser')
                date = self.sub_soup.find(class_ = 'article__time').get_text().replace('Release Date: ', '')
                # split into list of sentences
                for article in self.sub_soup.find_all(class_ = 'col-xs-12 col-sm-8 col-md-8'):
                    self.text = tokenize.sent_tokenize(article.get_text())

            # if it is post-article text, remove that sentence
            if 'Last update: ' in self.text[-1]:
                # deals with edge case of Jr. + (sth) being considered one sentence
                if 'Jr.\r' in self.text[-1]:
                    self.text[-1] = self.text[-1].partition('Jr.\r')[0] + self.text[-1].partition('Jr.\r')[1]
                elif 'Jr. \r' in self.text[-1]:
                    self.text[-1] = self.text[-1].partition('Jr. \r')[0] + self.text[-1].partition('Jr. \r')[1]
                else:
                    del self.text[-1]

            # append the list of sentences to remove \n\r\t
            text_list = []
            regex = re.compile(r'[\n\r\t]')
            for sub_text in self.text:
                text_list.append(re.sub(' +', ' ', regex.sub(' ', sub_text).strip()))

            # join the list of sentences together into a paragraph
            self.text = ''
            for sub_text in text_list:
                self.text = self.text + ' ' + sub_text
            self.text = self.text.replace(u'\xa0', u' ').strip()

            # remove header
            if 'For immediate release' in self.text:
                self.text = self.text.partition('For immediate release ')[2]

            # remove sentences that don't end with a period
            self.text = tokenize.sent_tokenize(self.text)
            if self.text[-1][-1] != '.':
                del self.text[-1]
            self.text = ' '.join(self.text)

            if self.convert_date(date) not in date_to_text:
                if self.convert_date(date) == '03/23/2020':
                    date_to_text['03/18/2020'] = self.text
                else:
                    date_to_text[self.convert_date(date)] = self.text

    def convert_date(self, date):
        try:
            return datetime.strptime(date, '%B %d, %Y').strftime('%m/%d/%Y')
        except ValueError:
            return datetime.strptime(date, '%b %d, %Y').strftime('%m/%d/%Y')

for i in range(1999, 2022):
    webscrapper = WebScrapper(str(i))

for date, text in date_to_text.items():
    if 'Voting for the ' in text:
        tuple = text.partition('Voting for the ')
        modified_text = tuple[1] + tuple[2]
        tuple = modified_text.partition('Voting against ')

        voting_for = tuple[0].strip()
        voting_against = tuple[1] + tuple[2]

        # universalize the beginning to 'Voting for the FOMC monetary policy action were:'
        regex = re.compile('Voting for(.*)were')
        voting_for = regex.sub('Voting for the FOMC monetary policy action were:', voting_for)
        # bunch of replacements
        voting_for = voting_for.replace('::', ':').replace('  ', ' ').replace(', Vice Chairman;', ';').replace(', Vice Chair;', ';').replace(', Chairman;', ';').replace(', Chair;', ';').replace(', Chair,', ';').replace(', Jr.', '').replace(', and', ';').replace(',', ';').replace('; and', ';').strip()
        # remove the beginning
        voting_for = tokenize.sent_tokenize(voting_for.partition('Voting for the FOMC monetary policy action were: ')[2])[0]

        # get last names
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

        # remove unnecessary endings
        voting_against = voting_against.partition(' In taking')[0].partition('In a related action, the Board of Governors ')[0].partition('1. The Open Market Desk will issue a technical note shortly after the statement providing operational details on how it will carry out these transactions.')[0]
        # split into sentences
        voting_against = tokenize.sent_tokenize(voting_against)
        # remove sentences that include the word alternate
        voting_against_sentence_list = []
        for sentence in voting_against:
            if 'alternate' not in sentence:
                voting_against_sentence_list.append(sentence)
        voting_against = ' '.join(voting_against_sentence_list)

        if voting_against == 'Voting against the action: none.':
            voting_against = ''

        # save the paragraph
        voting_against_paragraph = voting_against

        # parse to get names
        voting_against = [x for x in nlp(voting_against).ents if x.label_ == 'PERSON']

        # get last names
        last_name_list = []
        if voting_against != []:
            for name in voting_against:
                word_in_name_list = str(name).split(' ')
                if word_in_name_list[len(word_in_name_list) - 1] not in last_name_list:
                    last_name_list.append(word_in_name_list[len(word_in_name_list) - 1])
            voting_against = ', '.join(last_name_list)
        else:
            voting_against = ''
        if voting_against == '':
            number_voting_against = 0
        else:
            number_voting_against = len(voting_against.split(', '))

        date_to_text[date] = [number_voting_for, number_voting_against, voting_for, voting_against, voting_against_paragraph]

    else:
        date_to_text[date] = ['', '', '', '', '']

date_list = ['FOMC Statement Release Date']
statement_list = ['Statement Release Time']
press_conference_list = ['Press Conference Start Time']
sep_list = ['SEP Released']
minute_list = ['Minutes Release Date']
internal_material_list = ['Internal Material Released']
number_voting_for_list = ['Number of Members Voting in Favor']
number_voting_against_list = ['Number of Members Not in Favor']
voting_for_list= ['Names in Favor']
voting_against_list = ['Names Not in Favor']
voting_against_paragraph_list = ['Reason for Dissent']

for date, text in date_to_text.items():
    date_list.append(date)
    if date != '03/18/2020':
        statement_list.append('02:00 PM')
    if date in date_to_minute:
        minute_list.append(date_to_minute[date])
    internal_material_list.append('01' + '/' + str(int(date.split('/')[-1]) + 6))
    number_voting_for_list.append(text[0])
    number_voting_against_list.append(text[1])
    voting_for_list.append(text[2])
    voting_against_list.append(text[3])
    voting_against_paragraph_list.append(text[4])

try:
    FOMC_info_release_sheet = sheet.add_worksheet('fomc_info_release', rows = 187, cols = 11)
    FOMC_info_release_sheet.update_col(1, date_list)
    FOMC_info_release_sheet.update_col(2, statement_list)
    FOMC_info_release_sheet.update_col(3, press_conference_list)
    FOMC_info_release_sheet.update_col(4, sep_list)
    FOMC_info_release_sheet.update_col(5, minute_list)
    FOMC_info_release_sheet.update_col(6, internal_material_list)
    FOMC_info_release_sheet.update_col(7, number_voting_for_list)
    FOMC_info_release_sheet.update_col(8, number_voting_against_list)
    FOMC_info_release_sheet.update_col(9, voting_for_list)
    FOMC_info_release_sheet.update_col(10, voting_against_list)
    FOMC_info_release_sheet.update_col(11, voting_against_paragraph_list)
    FOMC_info_release_sheet.sort_range(start = 'A2', end = 'F187', basecolumnindex = 0, sortorder = 'ASCENDING')
    bold = FOMC_info_release_sheet.cell('A1')
    bold.set_text_format('bold', True)
    DataRange('A1','K1', worksheet = FOMC_info_release_sheet).apply_format(bold)
except:
    pass