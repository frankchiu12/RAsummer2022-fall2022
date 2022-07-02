import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random

class Equation():

    def __init__(self, relative_file_path, statistic):
        excel = pd.ExcelFile(relative_file_path)
        self.df = pd.read_excel(excel, statistic).dropna(subset = [statistic + 'F1'])
        self.year_list = self.df.DATE.unique()
        self.year_quarter_to_mean = {}

    def data(self, statistic):
        for year_quarter in self.year_list:
            if '-'.join(str(year_quarter).split('.')) not in self.year_quarter_to_mean:
                self.year_quarter_to_mean['-'.join(str(year_quarter).split('.'))] = np.mean(self.df.loc[self.df['DATE'].eq(year_quarter)][statistic + 'F1'].tolist())

        year_quarter_list = []
        statistic_list = []
        for year_quarter, mean in self.year_quarter_to_mean.items():
            year_quarter_list.append(year_quarter)
            statistic_list.append(mean)

        return year_quarter_list, statistic_list

def taylor_1993_equation(inflation, output_gap):
    return 1.25 + inflation + 0.5 * (inflation - 2) + 0.5 * output_gap

def taylor_1999_equation(inflation, output_gap):
    return 1.25 + inflation + 0.5 * (inflation - 2) + output_gap

# TODO: is it 1.25?
def inertial_taylor_1999_equation(inflation, output_gap, prev_ffr):
    return 0.85 * prev_ffr + 0.15 * (1.25 + inflation + 0.5 * (inflation - 2) + output_gap)

def first_difference_rule_equation(prev_ffr, three_quarter_ahead_inflation, three_quarter_ahead_change_in_output_gap):
    return prev_ffr + 0.5 * (three_quarter_ahead_inflation - 2) + 0.5 * (three_quarter_ahead_change_in_output_gap)

gPCPI = Equation('GBweb_Row_Format.xlsx', 'gPCPI').data('gPCPI')
year_quarter_list = gPCPI[0]
gPCPI_list = gPCPI[1]
random_list = []
taylor_1993_list = []
taylor_1999_list = []
inertial_taylor_1999_list = []
first_difference_list = []

for i in range(len(gPCPI_list)):
    random_list.append(random.randint(1, 30))
    taylor_1993_list.append(taylor_1993_equation(gPCPI_list[i], random_list[i]))
    taylor_1999_list.append(taylor_1999_equation(gPCPI_list[i], random_list[i]))
    inertial_taylor_1999_list.append(inertial_taylor_1999_equation(gPCPI_list[i], random_list[i], random_list[i]))
    first_difference_list.append(first_difference_rule_equation(random_list[i], gPCPI_list[i], random_list[i]))

plt.rcParams["figure.figsize"] = [12, 6]
plt.rcParams["figure.autolayout"] = True
plt.gcf().canvas.manager.set_window_title('FOMC Equations')
plt.plot(year_quarter_list, taylor_1993_list, color = 'red', linewidth = 2, label = 'Taylor 1993 Rule')
plt.plot(year_quarter_list, taylor_1999_list, color = 'blue', linewidth = 2, label = 'Taylor 1999 Rule')
plt.plot(year_quarter_list, inertial_taylor_1999_list, color = 'green', linewidth = 2, label = 'Inertial Taylor 1999 Rule')
plt.plot(year_quarter_list, first_difference_list, color = 'purple', linewidth = 2, label = 'First Difference Rule')
plt.title('Comparison of Projected FFR by FOMC Equations', fontweight = 'bold', backgroundcolor = 'silver')
plt.xlabel('YEAR_QUARTER')
plt.ylabel('ESTIMATED FFR')
plt.xticks(year_quarter_list[::8], rotation = 45)
plt.legend(loc = 'upper right')

plt.show()