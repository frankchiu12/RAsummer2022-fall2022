import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np

class Plot:

    def __init__(self, relative_file_path, statistic, is_growth, has_underscore):

        if (has_underscore):
            self.df = pd.read_excel(relative_file_path).dropna(subset=[statistic + '_3'])
        else:
            self.df = pd.read_excel(relative_file_path).dropna(subset=[statistic + '3'])
        self.year_list = self.df.YEAR.unique()
        self.quarter_list = [1, 2, 3, 4]
        self.year_to_quarter_to_statistic = {}
        self.year_quarter_list = []
        self.percentile_25th_list = []
        self.percentile_median_list = []
        self.percentile_75th_list = []
        if (has_underscore):
            self.data(statistic + '_', is_growth)
        else:
            self.data(statistic, is_growth)
        if (is_growth):
            self.plot(statistic.upper() + ' Annual Growth')
        else:
            self.plot(statistic.upper())

    def data(self, statistic, is_growth):

        for year in self.year_list:
            if year not in self.year_to_quarter_to_statistic:
                self.year_to_quarter_to_statistic[year] = {}
            for quarter in self.quarter_list:
                if quarter not in self.year_to_quarter_to_statistic[year]:
                    self.year_to_quarter_to_statistic[year][quarter] = self.df.loc[self.df['YEAR'].eq(year) & self.df['QUARTER'].eq(quarter)][statistic + '3'].tolist()

        for year in self.year_to_quarter_to_statistic:
            for quarter in self.year_to_quarter_to_statistic[year]:
                statistics_list = []
                if len(self.year_to_quarter_to_statistic[year][quarter]) > 0:
                    statistics_list.append(np.percentile(self.year_to_quarter_to_statistic[year][quarter], 25))
                    statistics_list.append(np.percentile(self.year_to_quarter_to_statistic[year][quarter], 50))
                    statistics_list.append(np.percentile(self.year_to_quarter_to_statistic[year][quarter], 75))
                self.year_to_quarter_to_statistic[year][quarter] = statistics_list

        year_quarter_to_statistic = {}
        for year in self.year_to_quarter_to_statistic:
            for quarter in self.year_to_quarter_to_statistic[year]:
                if str(int(year)) + '-' + str(quarter) not in year_quarter_to_statistic:
                    if len(self.year_to_quarter_to_statistic[year][quarter]) > 0:
                        year_quarter_to_statistic[str(int(year)) + '-' + str(quarter)] = self.year_to_quarter_to_statistic[year][quarter]

        if is_growth:
            year_quarter_to_statistic_copy = year_quarter_to_statistic.copy()
            year_quarter_to_pop_list = []
            for year_quarter, statistic in year_quarter_to_statistic_copy.items():
                past_year_int = int(year_quarter[:4]) - 1
                past_year_quarter = str(past_year_int) + year_quarter[4:]
                if past_year_quarter in year_quarter_to_statistic:
                    year_quarter_to_statistic_copy[year_quarter] = [(year_quarter_to_statistic[year_quarter][0] - year_quarter_to_statistic[past_year_quarter][0])/year_quarter_to_statistic[past_year_quarter][0], (year_quarter_to_statistic[year_quarter][1] - year_quarter_to_statistic[past_year_quarter][1])/year_quarter_to_statistic[past_year_quarter][1], (year_quarter_to_statistic[year_quarter][2] - year_quarter_to_statistic[past_year_quarter][2])/year_quarter_to_statistic[past_year_quarter][2]]
                else:
                    year_quarter_to_pop_list.append(year_quarter)

            for year_quarter in year_quarter_to_pop_list:
                year_quarter_to_statistic_copy.pop(year_quarter)

            year_quarter_to_statistic = year_quarter_to_statistic_copy

            for year_quarter, statistic in year_quarter_to_statistic.items():
                self.year_quarter_list.append(year_quarter)
                self.percentile_25th_list.append(statistic[0])
                self.percentile_median_list.append(statistic[1])
                self.percentile_75th_list.append(statistic[2])

        else:
            for year_quarter, statistic in year_quarter_to_statistic.items():
                self.year_quarter_list.append(year_quarter)
                self.percentile_25th_list.append(statistic[0])
                self.percentile_median_list.append(statistic[1])
                self.percentile_75th_list.append(statistic[2])

    def plot(self, statistic):

        # NOTE: dark mode: plt.style.use("dark_background")
        plt.rcParams["figure.figsize"] = [13, 6.5]
        plt.rcParams["figure.autolayout"] = True
        plt.gcf().canvas.manager.set_window_title(statistic)
        plt.suptitle(statistic + ' Expectations One Quarter Ahead Plots', fontweight = 'bold', backgroundcolor = 'silver')

        for i in range(1, 5):
            plt.subplot(2, 2, i)
            plt.tight_layout()

        plt.subplot(2, 2, 1).plot(self.year_quarter_list, self.percentile_25th_list, color = 'red', linewidth = 2)
        plt.subplot(2, 2, 1).set_title('25th Percentile ' + statistic + ' Expectations One Quarter Ahead', loc = 'left')
        plt.subplot(2, 2, 2).plot(self.year_quarter_list, self.percentile_median_list, color = 'blue', linewidth = 2)
        plt.subplot(2, 2, 2).set_title('Median ' + statistic + ' Expectations One Quarter Ahead', loc = 'left')
        plt.subplot(2, 2, 3).plot(self.year_quarter_list, self.percentile_75th_list, color = 'green', linewidth = 2)
        plt.subplot(2, 2, 3).set_title('75th Percentile ' + statistic + ' Expectations One Quarter Ahead', loc = 'left')
        plt.subplot(2, 2, 4).plot(self.year_quarter_list, self.percentile_25th_list, color = 'red', linewidth = 2, label = '25th Percentile')
        plt.subplot(2, 2, 4).plot(self.year_quarter_list, self.percentile_median_list, color = 'blue', linewidth = 2, label = 'Median')
        plt.subplot(2, 2, 4).plot(self.year_quarter_list, self.percentile_75th_list, color = 'green', linewidth = 2, label = '75th Percentile')
        plt.subplot(2, 2, 4).set_title('Comparison of ' + statistic + ' Expectations One Quarter Ahead', loc = 'left')
        plt.subplot(2, 2, 4).legend(loc = 'upper right')

        for i in range(1, 5):
            plt.subplot(2, 2, i).set_xlabel('YEAR-QUARTER')
            plt.subplot(2, 2, i).xaxis.labelpad = 10
            plt.subplot(2, 2, i).set_ylabel(statistic)
            plt.subplot(2, 2, i).set_xticks(self.year_quarter_list[::16])
            plt.subplot(2, 2, i).set_xticklabels(self.year_quarter_list[::16], rotation = 45)
            plt.subplot(2, 2, i).yaxis.set_major_locator(MaxNLocator(nbins = 6, integer = True))

        plt.show()

try:
    os.system('cls' if os.name == 'nt' else 'clear')
    # RGDP
    Plot('spf_plot_data/Individual_RGDP.xlsx', 'RGDP', False, False)
    # RGDP Growth
    Plot('spf_plot_data/Individual_RGDP.xlsx', 'RGDP', True, False)
    # PRGDP
    Plot('spf_plot_data/Individual_PRGDP.xlsx', 'PRGDP', False, False)
    # CPI
    Plot('spf_plot_data/Individual_CPI.xlsx', 'CPI', False, False)
    # CORECPI
    Plot('spf_plot_data/Individual_CORECPI.xlsx', 'CORECPI', False, False)
    # PCE
    Plot('spf_plot_data/Individual_PCE.xlsx', 'PCE', False, False)
    # COREPCE
    Plot('spf_plot_data/Individual_COREPCE.xlsx', 'COREPCE', False, False)
    # RR1_TBILL_PGDP
    Plot('spf_plot_data/Individual_RR1_TBILL_PGDP.xlsx', 'RR1_TBILL_PGDP', False, True)
    # SPR_TBOND_TBILL
    Plot('spf_plot_data/Individual_SPR_TBOND_TBILL.xlsx', 'SPR_Tbond_Tbill', False, False)
except:
    pass