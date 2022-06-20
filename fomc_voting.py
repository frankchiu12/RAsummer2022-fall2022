import os
import re

str_to_parse = ''

def parse_voting_for():
    voting_for = str_to_parse.partition('Voting for the FOMC monetary policy action were: ')[2]
    voting_for = re.sub(',.*?;', '; ', voting_for)
    voting_for = voting_for.split('; ')

    last_name_list = []
    for name in voting_for:
        word_in_name_list = name.split(' ')
        if '' in word_in_name_list:
            word_in_name_list.remove('')
        if 'Jr.' in word_in_name_list:
            word_in_name_list.remove('Jr.')
        last_name_list.append(word_in_name_list[len(word_in_name_list) - 1]) 

    parsed_last_name_list = []
    for last_name in last_name_list:
        parsed_last_name_list.append(last_name.strip(',.')) 

    print(str(len(parsed_last_name_list)) + '\n')
    print(', '.join(parsed_last_name_list) + '\n')

os.system('cls' if os.name == 'nt' else 'clear')
parse_voting_for()