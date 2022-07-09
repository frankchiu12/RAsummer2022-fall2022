import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

df = pd.read_excel('FOMC_equation.xlsx')
event_list = list(df.columns)
date_list = df[event_list[0]].to_list()
del event_list[0]
# NOTE: show Amy
event_list.remove('Lower NAIRU')
event_list.remove('Faster/Slower Productivity Growth')
event_list.remove('Taylor without/with Error')
event_list.remove('Realized Inflation')

begin_date_list = []
end_date_list = []
begin_decimal_list = []
for event in event_list:
    column_value_list = df[event].dropna().to_list()
    begin_index = df.index[df[event] == column_value_list[0]].to_list()[0]
    begin_date_list.append(datetime.strptime(date_list[begin_index], '%m/%d/%Y'))
    end_index = df.index[df[event] == column_value_list[-1]].to_list()[-1]
    end_date_list.append(datetime.strptime(date_list[end_index], '%m/%d/%Y'))

for date in begin_date_list:
    begin_decimal_list.append((date - datetime(1999, 1, 1)).days/365 + 1999)

difference_list = [(i - j).days/365 for i, j in zip(end_date_list, begin_date_list)]

event_to_begin_date = {}
event_to_end_date = {}
event_to_begin_decimal = {}
event_to_difference = {}

for i in range(len(event_list)):
    if event_list[i] not in event_to_begin_date:
        event_to_begin_date[event_list[i]] = begin_date_list[i].strftime("%m/%d/%Y")
    if event_list[i] not in event_to_end_date:
        event_to_end_date[event_list[i]] = end_date_list[i].strftime("%m/%d/%Y")
    if event_list[i] not in event_to_begin_decimal:
        event_to_begin_decimal[event_list[i]] = begin_decimal_list[i]
    if event_list[i] not in event_to_difference:
        event_to_difference[event_list[i]] = difference_list[i]

# sorted based on when the rules were introduced; for rules that all start at the same time, ordered based on when they ended first
event_to_begin_decimal_and_end_date = {}
for event in event_list:
    if event not in event_to_begin_decimal_and_end_date:
        event_to_begin_decimal_and_end_date[event] = [event_to_begin_decimal[event], event_to_end_date[event]]

event_to_begin_decimal_and_end_date = dict(sorted(event_to_begin_decimal_and_end_date.items(), key = lambda item: (item[1][0], datetime.strptime(item[1][1], '%m/%d/%Y')), reverse = True))

event_list = []
begin_date_list = []
end_date_list = []
begin_decimal_list = []
difference_list = []
for event in event_to_begin_decimal_and_end_date:
    event_list.append(event)
    begin_date_list.append(event_to_begin_date[event])
    if '12/14/2016' in event_to_end_date[event]:
        end_date_list.append(event_to_end_date[event] + ' (now)')
    else:
        end_date_list.append(event_to_end_date[event])
    begin_decimal_list.append(event_to_begin_decimal[event])
    difference_list.append(event_to_difference[event])

plt.rcParams["figure.figsize"] = [12, 6]
plt.rcParams["figure.autolayout"] = True
plt.gcf().canvas.manager.set_window_title('Timeline')
bar_graph = plt.barh(event_list, difference_list, left = begin_decimal_list, color = ['aquamarine', 'cornflowerblue'])

i = 0
for bar in bar_graph:
    plt.text(bar.get_x() + difference_list[i]/2, bar.get_y() + 0.325, (begin_date_list[i]) + ' - ' + end_date_list[i], ha = 'center', fontsize = 7)
    i += 1

plt.title('FOMC Equations Timeline', fontweight = 'bold', backgroundcolor = 'silver')
plt.xlabel('YEAR', labelpad = 10)
plt.ylabel('FOMC EQUATION', labelpad = 10)
plt.xticks([1999, 2001, 2003, 2005, 2007, 2009, 2011, 2013, 2015])
plt.show()