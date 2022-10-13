import csv
import pandas as pd
import matplotlib.pyplot as plt

csv_df = pd.read_csv('other_data/fomcdrafts_updating.csv', usecols = ['date', 'draftstatement', 'draftlabel'])

date_to_count = {}
date_list = []
count_list = []

for index, row in csv_df.iterrows():
    date = row['date']
    if date not in date_to_count:
        date_to_count[date] = 1
    else:
        date_to_count[date] += 1

date_to_count.popitem()

for date, count in date_to_count.items():
    date_list.append(date)
    count_list.append(count)

plt.rcParams["figure.figsize"] = [12, 6]
plt.rcParams["figure.autolayout"] = True
plt.gcf().canvas.manager.set_window_title('FOMC Alternatives Count')

plt.bar(date_list, count_list, color ='cornflowerblue', width = 0.4)
plt.title('FOMC Alternatives Count', fontweight = 'bold', backgroundcolor = 'silver')
plt.xlabel('MEETING DATE', labelpad = 10)
plt.ylabel('ALTERNATIVE COUNTS', labelpad = 10)
plt.xticks(date_list[::8], rotation = 45)
plt.show()

with open('/Users/franksi-unchiu/Desktop/cs200python/RAsummer2022/alternative_counts.csv', 'w') as f:
    writer = csv.writer(f)
    header_row = ['date', 'count of alternatives']
    writer.writerow(header_row)
    for i in range(len(date_list)):
        writer.writerow([date_list[i], count_list[i]])