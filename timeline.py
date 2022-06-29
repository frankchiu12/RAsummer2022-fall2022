import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

df = pd.read_excel('FOMCequation.xlsx')
event_list = list(df.columns)
date_list = df[event_list[0]].to_list()
del event_list[0]
# NOTE: show Amy
event_list.remove('Lower NAIRU')
event_list.remove('Faster/Slower Productivity Growth')
event_list.remove('Taylor without/with Error')
event_list.remove('Realized Inflation')

begin_list = []
end_list = []
for event in event_list:
    column_value_list = df[event].dropna().to_list()
    begin_index = df.index[df[event] == column_value_list[0]].to_list()[0]
    begin_list.append(datetime.strptime(date_list[begin_index], '%m/%d/%Y'))
    end_index = df.index[df[event] == column_value_list[-1]].to_list()[-1]
    end_list.append(datetime.strptime(date_list[end_index], '%m/%d/%Y'))

begin_time_list = []
for date in begin_list:
    begin_time_list.append((date - datetime(1999, 1, 1)).days/365 + 1999)

difference_list = [(i - j).days/365 for i, j in zip(end_list, begin_list)]

event_to_begin = {}
for i in range(len(event_list)):
    if event_list[i] not in event_to_begin:
        event_to_begin[event_list[i]] = begin_list[i].strftime("%m/%d/%Y")

even_to_end = {}
for i in range(len(event_list)):
    if event_list[i] not in even_to_end:
        if '12/31/2016' in end_list[i].strftime("%m/%d/%Y"):
            even_to_end[event_list[i]] = 'now'
        else:
            even_to_end[event_list[i]] = end_list[i].strftime("%m/%d/%Y")

event_to_begin_time = {}
for i in range(len(event_list)):
    if event_list[i] not in event_to_begin_time:
        event_to_begin_time[event_list[i]] = begin_time_list[i]

event_to_difference = {}
for i in range(len(event_list)):
    if event_list[i] not in event_to_difference:
        event_to_difference[event_list[i]] = difference_list[i]

event_to_difference = dict(sorted(event_to_difference.items(), key=lambda item: item[1], reverse=True))

event_list = []
difference_list = []
begin_time_list = []
begin_list = []
end_list = []
for event, difference in event_to_difference.items():
    event_list.append(event)
    difference_list.append(difference)
    begin_time_list.append(event_to_begin_time[event])
    begin_list.append(event_to_begin[event])
    end_list.append(even_to_end[event])

def addlabel(x, y):
    for i in range(len(begin_time_list)):
        plt.text(begin_time_list[i] + difference_list[i]/2, i, (x[i]) + ' - ' + y[i], ha = 'center', fontsize = 7)

plt.rcParams["figure.figsize"] = [12, 6]
plt.rcParams["figure.autolayout"] = True
plt.gcf().canvas.manager.set_window_title('Timeline')
bar_graph = plt.barh(event_list, difference_list, left=begin_time_list, color = ['springgreen', 'cornflowerblue'])
plt.title('FOMC Equations Timeline', fontweight = 'bold', backgroundcolor = 'silver')
plt.xlabel('YEAR')
plt.ylabel('FOMC EQUATION')
plt.xticks([1999, 2001, 2003, 2005, 2007, 2009, 2011, 2013, 2015])
addlabel(begin_list, end_list)
plt.show()