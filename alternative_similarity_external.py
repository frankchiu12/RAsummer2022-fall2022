import csv
import pandas as pd
from pytest import skip
import spacy
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import statistics

nlp = spacy.load('en_core_web_sm')
csv_df = pd.read_csv('other_data/fomcdrafts_updating.csv', usecols = ['date', 'draftstatement', 'draftlabel'])
date_to_label_to_statement = {}
date_to_vector = {}
date_to_cosine = {}
date_to_row = {}
skip_date_list = []
all_statement_list = []

for index, row in csv_df.iterrows():
    date = row['date']
    label = row['draftlabel']

    lemmatized_statements = []
    statement = row['draftstatement']
    if isinstance(statement, float):
        break
    statement = statement.replace('funds rate', 'funds_rate').replace('points', 'point').replace('basis point', 'bp')
    statement = statement.replace('Federal open market committee', 'fomc').replace('Federal Open Market Committee','FOMC').replace('federal open market committee', 'FOMC').replace('Federal Reserve', 'FedRes').replace('federal reserve', 'FedRes')
    doc = nlp(statement)
    lemmatized_doc = ' '.join([token.lemma_ for token in doc])
    lemmatized_statements.append(lemmatized_doc)

    punctuation = str.maketrans('', '', '!"#$%\'()*+,./:;<=>?@[\\]^_{|}~&1234567890-’')
    keep = ['above', 'under', 'more', 'over', 'not', 'below', 'down', 'up', 'against', 'down', 'off', 'both', 'once', 'while', 'again', 'after', 'only', 'during', 'further','until']
    fed_spec_stopwords =['committee', 'committees', 'met', 'january', 'februrary', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december', 'today', 'federal', 'open', 'market', 'percent']
    stop_words = set(stopwords.words('english')) - set(keep) 
    stop_words = set([word for word in stop_words] + fed_spec_stopwords)

    first_clean = []
    for statement in lemmatized_statements:
        statement = statement.lower()
        statement = ''.join([x.translate(punctuation) for x in statement if x])
        statement = ' '.join([word for word in statement.split() if word.lower() not in stop_words])
        statement = statement.replace('long run', 'long_run').replace('long term', 'long_run').replace('short run', 'short_run').replace('short term', 'short_run').replace('medium run', 'medium_run').replace('medium term', 'medium_run').replace('near run', 'near_term').replace('near term', 'near_term')
        statement =statement.replace('mortgage backed securities','mb_securities').replace('mortgage back securities','mb_securities').replace('mortgage back','mortgage_backed').replace('monetary policy','monetary_policy').replace('maximum employment','maximum_employment')
        first_clean.append(statement)
        statement = ' '.join(first_clean)

    if date not in date_to_label_to_statement:
        date_to_label_to_statement[date] = {}
    if label not in date_to_label_to_statement[date]:
        date_to_label_to_statement[date][label] = statement

for date, statement in date_to_label_to_statement.items():
    if 'A' not in statement:
        skip_date_list.append(date)
        continue
    else:
        A = statement['A']
    if 'B' not in statement:
        skip_date_list.append(date)
        continue
    else:
        B = statement['B']
    if 'C' not in statement:
        skip_date_list.append(date)
        continue
    else:
        C = statement['C']
    all_statement_list.extend([A, B, C])

vectorizer = TfidfVectorizer(lowercase = True, ngram_range = (1,1), use_idf = True) 
X = vectorizer.fit_transform(all_statement_list)
features = vectorizer.get_feature_names_out()
df_tfidfvect = pd.DataFrame(data = X.toarray(), columns = features)

counter = 0
for date, statement in date_to_label_to_statement.items():
    if date not in date_to_vector and date not in skip_date_list:
        new_df = df_tfidfvect.iloc[[counter, counter + 1, counter + 2],:] 
        date_to_vector[date] = new_df
        counter += 3

for date, vector in date_to_vector.items():
    cosine_df = pd.DataFrame(cosine_similarity(vector, dense_output = True))
    if date not in date_to_cosine:
        date_to_cosine[date] = cosine_df

with open('/Users/franksi-unchiu/Desktop/cs200python/RAsummer2022/tf_idf_cosine_statements_external.csv', 'w') as f:
    writer = csv.writer(f)
    header_row = ['date', 'A to B', 'A to C', 'B to C', 'maximum', 'minimum', 'mean', 'median']
    writer.writerow(header_row)
    for date, cosine in date_to_cosine.items():
        row1 = cosine.loc[cosine.index[0]]
        row2 = cosine.loc[cosine.index[1]]
        A_B = row1[1]
        A_C = row1[2]
        B_C = row2[2]
        maximum = max(A_B, A_C, B_C)
        minimum = min(A_B, A_C, B_C)
        mean = (A_B + A_C + B_C) / 3
        median = statistics.median([A_B, A_C, B_C])
        row = [A_B, A_C, B_C, maximum, minimum, mean, median]
        row.insert(0, date)
        writer.writerow(row)