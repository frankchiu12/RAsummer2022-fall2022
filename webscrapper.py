import requests
from bs4 import BeautifulSoup, NavigableString
import re
from nltk import tokenize
from datetime import datetime
import spacy
import pygsheets
from pygsheets.datarange import DataRange

sheet = pygsheets.authorize(service_account_file = 'write_into_google_sheet.json').open('Summer RA')
nlp = spacy.load('en_core_web_md')
date_to_press_conference = {}
date_to_SEP = {}
date_to_minutes = {}
date_to_text = {}
date_to_voting = {}

class WebScrapper():

    def __init__(self, year):
        if int(year) < 2017:
            URL = 'https://www.federalreserve.gov/monetarypolicy/fomchistorical' + year + '.htm'
        else:
            URL = 'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm'
        page = requests.get(URL)
        self.soup = BeautifulSoup(page.content, 'html.parser')
        self.statement_url_list = []
        self.text = ''
        # TODO: might not need this
        self.date = ''

        if int(year) <= 2017:
            self.get_press_conference_and_SEP(year)
            self.get_minutes(year)
            self.get_statement_url(year)
            self.get_text(year)

    def get_press_conference_and_SEP(self, year):
        if int(year) < 2011:
            self.get_press_conference_and_SEP_helper('panel panel-default')
        elif 2011 <= int(year) < 2017:
            self.get_press_conference_and_SEP_helper('panel panel-default panel-padded')
        # TODO: redo
        else:
            for meeting_year in self.soup.find(id = 'article').find_all(class_ = 'panel panel-default'):
                for meeting in meeting_year:
                    date = ''
                    if isinstance(meeting, NavigableString):
                        continue
                    if '(notation value)' in meeting.get_text() or '(unscheduled)' in meeting.get_text():
                        continue
                    if 'panel-heading' in meeting.get('class'):
                        self.date = meeting.get_text().split(' ')[0]
                    for meeting_information in meeting:
                        press = False
                        sep = False
                        if isinstance(meeting_information, NavigableString):
                            continue
                        if meeting_information.get('class') is not None and 'fomc-meeting__month' in meeting_information.get('class'):
                            date = meeting_information.get_text()
                        if meeting_information.get('class') is not None and 'fomc-meeting__date' in meeting_information.get('class'):
                            date = date + ' ' + meeting_information.get_text() + ' ' + self.date
                        if meeting_information.get('class')is not None and 'col-lg-3' in meeting_information.get('class'):
                            if 'Press Conference' in meeting_information.get_text():
                                press = 'TRUE'
                            else:
                                press = ''
                            if 'Projection Materials' in meeting_information.get_text():
                                sep = 'TRUE'
                            else:
                                sep = ''
                        date = date.split(' ')
                        if len(date) != 3:
                            date = ' '.join(date)
                            continue
                        date_word_list = []
                        for date_word in date:
                            if '-' in date_word:
                                date_word = date_word.partition('-')[2]
                            if '*' in date_word:
                                date_word = date_word.strip('*')
                            if '/' in date_word:
                                date_word = date_word.partition('/')[2]
                            date_word_list.append(date_word)
                        date_word_list[1] = date_word_list[1] + ','
                        date = ' '.join(date_word_list).replace(',,,,', ',').replace(',,,', ',')
                        if '(notation value)' not in date and '(cancelled)' not in date:
                            if date not in date_to_press_conference and press != False:
                                date_to_press_conference[self.convert_date(date)] = press
                            if date not in date_to_SEP and sep != False:
                                date_to_SEP[self.convert_date(date)] = sep

    def get_date_helper(self, meeting):
        date = meeting.find('h5').get_text().partition('Meeting - ')
        date = ''.join(date[0] + date[2]).split(' ')
        date_word_list = []
        if len(date) == 5:
            date_word_list.append(date[1].partition('-')[2] + ' ' + date[2] + ',')
            date_word_list.append(date[4])
        else:
            date[1] = date[1] + ','
            for date_word in date:
                if '/' in date_word:
                    date_word = date_word.split('/')[1]
                if '-' in date_word:
                    date_word = date_word.split('-')[1]
                date_word_list.append(date_word)
        date = self.convert_date(' '.join(date_word_list))
        return date

    def get_press_conference_and_SEP_helper(self, HTML_class):
        for meeting in self.soup.find(id = 'article').find_all(class_ = HTML_class):
            if 'Meeting' not in meeting.find('h5').get_text() or 'Statement' not in meeting.get_text():
                continue
            date = self.get_date_helper(meeting)
            for column in meeting.find_all(class_ = 'col-xs-12 col-md-6'):
                if 'Press' in column.get_text():
                    if date not in date_to_press_conference:
                        date_to_press_conference[date] = 'TRUE'  
                else:
                    if date not in date_to_press_conference:
                        date_to_press_conference[date] = ''
                if 'SEP' in column.get_text():
                    date_to_SEP[date] = 'TRUE'
                else:
                    date_to_SEP[date] = ''

    def get_minutes(self, year):
        if int(year) < 2011:
            self.get_minutes_helper('panel panel-default')
        elif 2011 <= int(year) < 2017:
            self.get_minutes_helper('panel panel-default panel-padded')
        # TODO: redo
        else:
            for meeting_year in self.soup.find(id = 'article').find_all(class_ = 'panel panel-default'):
                for meeting in meeting_year:
                    date = ''
                    if isinstance(meeting, NavigableString):
                        continue
                    if '(notation value)' in meeting.get_text() or '(unscheduled)' in meeting.get_text():
                        continue
                    if 'panel-heading' in meeting.get('class'):
                        self.date = meeting.get_text().split(' ')[0]
                    for meeting_information in meeting:
                        minute = ''
                        if isinstance(meeting_information, NavigableString):
                            continue
                        if meeting_information.get('class') is not None and 'fomc-meeting__month' in meeting_information.get('class'):
                            date = meeting_information.get_text()
                        if meeting_information.get('class') is not None and 'fomc-meeting__date' in meeting_information.get('class'):
                            date = date + ' ' + meeting_information.get_text() + ' ' + self.date
                        if meeting_information.get('class')is not None and 'fomc-meeting__minutes' in meeting_information.get('class'):
                            minute = re.findall('Released (.*?)\)', meeting_information.get_text())
                        date = date.split(' ')
                        if len(date) != 3:
                            date = ' '.join(date)
                            continue
                        date_word_list = []
                        for date_word in date:
                            if '-' in date_word:
                                date_word = date_word.partition('-')[2]
                            if '*' in date_word:
                                date_word = date_word.strip('*')
                            if '/' in date_word:
                                date_word = date_word.partition('/')[2]
                            date_word_list.append(date_word)
                        if ',' not in date_word_list[1]:
                            date_word_list[1] = date_word_list[1] + ','
                        date = ' '.join(date_word_list)
                        if '(notation value)' not in date and '(cancelled)' not in date:
                            if date not in date_to_minutes:
                                if minute != '' and minute != []:
                                    date_to_minutes[self.convert_date(date)] = self.convert_date(minute[0])
                                else:
                                    date_to_minutes[self.convert_date(date)] = ''

    def get_minutes_helper(self, HTML_class):
        for meeting in self.soup.find(id = 'article').find_all(class_ = HTML_class):
            if 'Meeting' not in meeting.find('h5').get_text() or 'Statement' not in meeting.get_text():
                continue
            date = self.get_date_helper(meeting)
            for column in meeting.find_all(class_ = 'col-xs-12 col-md-6'):
                for p in column.find_all('p'):
                    for a in p.find_all('a', href = True):
                        if 'minutes' in a.get('href'):
                            if date not in date_to_minutes:
                                if re.findall('Released (.*?)\)', p.get_text()) != []:
                                    date_to_minutes[date] = self.convert_date(re.findall('Released (.*?)\)', p.get_text())[0])

######################################################################################################################################

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
                # split into list of sentences
                for article in sub_soup.find_all('td'):
                    self.text = tokenize.sent_tokenize(article.get_text())
            else: 
                date = sub_soup.find(class_ = 'article__time').get_text().replace('Release Date: ', '')
                # split into list of sentences
                for article in sub_soup.find_all(class_ = 'col-xs-12 col-sm-8 col-md-8'):
                    self.text = tokenize.sent_tokenize(article.get_text())

            # if there is post-article text, remove that sentence
            if 'Last update: ' in self.text[-1]:
                # deals with the edge case of Jr. + (something) being considered one sentence
                if 'Jr.\r' in self.text[-1]:
                    self.text[-1] = self.text[-1].partition('Jr.\r')[0] + self.text[-1].partition('Jr.\r')[1]
                elif 'Jr. \r' in self.text[-1]:
                    self.text[-1] = self.text[-1].partition('Jr. \r')[0] + self.text[-1].partition('Jr. \r')[1]
                else:
                    del self.text[-1]

            # substitute + and \n\r\t with a space for each element in the list of sentences and strip
            text_list = []
            for sub_text in self.text:
                text_list.append(re.sub(' +', ' ', re.compile(r'[\n\r\t]').sub(' ', sub_text).strip()))

            # join the list of sentences together into a paragraph
            self.text = ''
            for sub_text in text_list:
                self.text = self.text + ' ' + sub_text
            # replace \xao with a space and strip
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

for year in range(1999, 2023):
    webscrapper = WebScrapper(str(year))

######################################################################################################################################

for date, text in date_to_text.items():
    if 'Voting for the ' in text:
        tuple = text.partition('Voting for the ')
        modified_text = tuple[1] + tuple[2]
        tuple = modified_text.partition('Voting against ')

        voting_for = tuple[0].strip()
        voting_against = tuple[1] + tuple[2]

        # universalize the beginning to 'Voting for the FOMC monetary policy action were:'
        voting_for = re.compile('Voting for(.*)were').sub('Voting for the FOMC monetary policy action were:', voting_for)
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
        # parse the paragraph to get names
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
        press_conference_list.append(date_to_press_conference[date])
        sep_list.append(date_to_SEP[date])
        minute_list.append(date_to_minutes[date])
        internal_material_list.append('01' + '/' + str(int(date.split('/')[-1]) + 6))
    else:
        statement_list.append('')
        press_conference_list.append('')
        sep_list.append('')
        minute_list.append('')
        internal_material_list.append('')

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
    FOMC_info_release_sheet.sort_range(start = 'A2', end = 'K187', basecolumnindex = 0, sortorder = 'ASCENDING')
    bold = FOMC_info_release_sheet.cell('A1')
    bold.set_text_format('bold', True)
    DataRange('A1','K1', worksheet = FOMC_info_release_sheet).apply_format(bold)
except:
    pass