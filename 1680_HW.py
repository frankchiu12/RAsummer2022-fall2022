import os
import csv
import pandas as pd

folder_path = 'other_data'
file_reader = open(os.path.join(folder_path, 'US-Economic-News.csv'), 'r', encoding = 'unicode_escape')
csv_reader = csv.reader(file_reader)
file_writer = open(os.path.join(folder_path, 'Subset_US_Economic_News.csv'), 'w', encoding = 'unicode_escape', newline = '')
csv_writer  = csv.writer(file_writer)
ac_header = next(csv_reader)

csv_writer.writerow(ac_header)
for index, ac_row in enumerate(csv_reader):
    if index < 800:
        csv_writer.writerow(ac_row)

file_reader.close()
file_writer.close()

df_news = pd.read_csv(os.path.join(folder_path, 'Subset_US_Economic_News.csv'), encoding = 'unicode_escape')
df_news['date'] = pd.to_datetime(df_news['date'])

df_b = df_news[['date', 'headline', 'text']]

US_counter = 0
us_counter = 0
for headline in df_news['headline']:
    if 'US' in headline:
        US_counter += 1
    if 'us' in headline:
        us_counter += 1
print(US_counter)
print(us_counter)

# in one of them us is capitalized and an independent word

import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

stops = set(stopwords.words('english'))
table_punctuation = str.maketrans('', '', '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~') 

token_list=[]
for i, row in enumerate(df_news['text']):
    text = row.translate(table_punctuation)
    tokens = [word.lower() for word in nltk.tokenize.word_tokenize(text) if word.lower() not in stops]
    token_list.append(tokens)

df_news['tokens'] = token_list

monetary_policy_word_list= ['monetary', 'fed ', 'federal reserve', 'Federal Reserve', 'Monetary']

tally = 0
monetary_text = []
for row in df_news['text']:
    mon = 0
    if any(keyword in row for keyword in monetary_policy_word_list):
        tally += 1
        mon = 1
    monetary_text.append(mon)
print(tally)
df_news['monetary_flag'] = monetary_text

df_monetary_news = df_news[df_news['monetary_flag'] == 1]
df_nonmonetary_news = df_news[df_news['monetary_flag'] != 1]

from collections import Counter

top_N = 15
monetary_news_words = [word for token_list in df_monetary_news['tokens'].tolist() for word in token_list]
top_words = pd.DataFrame(Counter(monetary_news_words).most_common(top_N), columns = ['Word', 'Count']).set_index('Word')
print(top_words)

top_N = 15
nonmonetary_news_words = [word for token_list in df_nonmonetary_news['tokens'].tolist() for word in token_list]
top_words = pd.DataFrame(Counter(nonmonetary_news_words).most_common(top_N), columns = ['Word', 'Count']).set_index('Word')
print(top_words)

# don't have words in monetary_policy_wordlist

from wordcloud import WordCloud
import matplotlib.pyplot as plt

all_words=' '.join(monetary_news_words)
word_cloud = WordCloud(collocations = False, background_color = 'white').generate(all_words)

plt.imshow(word_cloud, interpolation = 'bilinear')
plt.axis('off')
plt.title('Word Cloud for US Economics Articles')
plt.show()

all_words=' '.join(nonmonetary_news_words)
word_cloud = WordCloud(collocations = False, background_color = 'white').generate(all_words)

plt.imshow(word_cloud, interpolation = 'bilinear')
plt.axis('off')
plt.title('Word Cloud for US Economics Articles')
plt.show()

# similar