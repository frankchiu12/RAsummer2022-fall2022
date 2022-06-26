import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

event_list = ['Taylor 1993, Taylor 1999, First-Difference', 'Inertial Taylor 1999', 'Outcome-Based', 'Greenbook Forecast-Based, FOMC Forecast-Based, TIPS-Based', 'Nominal Income Targeting', 'Forecast-Based', 'Taylor 1999 with Higher r*']
begin_list = np.array([datetime(2004, 1, 28), datetime(2012, 9, 13), datetime(2004, 1, 28), datetime(2004, 1, 28), datetime(2012, 3, 13), datetime(2006, 1, 31), datetime(2006, 8, 8)])
end_list = np.array([datetime(2016, 12, 31), datetime(2016, 12, 31), datetime(2012, 12, 17), datetime(2005, 12, 13), datetime(2014, 12, 17), datetime(2012, 1, 25), datetime(2008, 4, 30)])

begin_time_list = []
for date in begin_list:
    begin_time_list.append((date - datetime(2004, 1, 1)).days/365 + 2004)

print(begin_time_list)

difference_list = [(i - j).days/365 for i, j in zip(end_list, begin_list)]

event_to_begin = {}
for i in range(len(event_list)):
    if event_list[i] not in event_to_begin:
        if '01/28/2004' not in begin_list[i].strftime("%m/%d/%Y"):
            event_to_begin[event_list[i]] = begin_list[i].strftime("%m/%d/%Y")
        else:
            event_to_begin[event_list[i]] = str(begin_list[i].year)

even_to_end = {}
for i in range(len(event_list)):
    if event_list[i] not in even_to_end:
        if '12/31' not in end_list[i].strftime("%m/%d/%Y"):
            even_to_end[event_list[i]] = end_list[i].strftime("%m/%d/%Y")
        elif '12/31/2016' in end_list[i].strftime("%m/%d/%Y"):
            even_to_end[event_list[i]] = 'now'
        else:
            even_to_end[event_list[i]] = 'eoy ' + str(end_list[i].year)

event_to_begin_year = {}
for i in range(len(event_list)):
    if event_list[i] not in event_to_begin_year:
        event_to_begin_year[event_list[i]] = begin_time_list[i]

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
    begin_time_list.append(event_to_begin_year[event])
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
addlabel(begin_list, end_list)
plt.show()