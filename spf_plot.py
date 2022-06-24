import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np

class Plot:

    def __init__(self, relative_file_path, statistic, statistic_in_words, is_growth, has_underscore):

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
            self.plot(statistic.upper() + ' Annual Growth', statistic_in_words + ' Annual Growth')
        else:
            self.plot(statistic.upper(), statistic_in_words)

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

    def plot(self, statistic, statistic_in_words):

        # NOTE: dark mode: plt.style.use("dark_background")
        plt.rcParams["figure.figsize"] = [13, 6.5]
        plt.rcParams["figure.autolayout"] = True
        plt.gcf().canvas.manager.set_window_title(statistic_in_words)
        plt.suptitle(statistic_in_words + ' Expectations One Quarter Ahead Plots', fontweight = 'bold', backgroundcolor = 'silver')

        for i in range(1, 7):
            plt.subplot(2, 3, i)
            plt.tight_layout()
            plt.labelsize = 10

        plt.subplot(2, 3, 1).plot(self.year_quarter_list, self.percentile_25th_list, color = 'red', linewidth = 2, linestyle = 'dashed')
        plt.subplot(2, 3, 1).set_title('25th Percentile', loc = 'left')

        plt.subplot(2, 3, 2).plot(self.year_quarter_list, self.percentile_median_list, color = 'blue', linewidth = 2)
        plt.subplot(2, 3, 2).set_title('Median', loc = 'left')

        plt.subplot(2, 3, 3).plot(self.year_quarter_list, self.percentile_75th_list, color = 'green', linewidth = 2, linestyle = 'dashed')
        plt.subplot(2, 3, 3).set_title('75th Percentile', loc = 'left')

        plt.subplot(2, 3, 4).plot(self.year_quarter_list, self.percentile_25th_list, color = 'red', linewidth = 2, linestyle = 'dashed', label = '25th Percentile')
        plt.subplot(2, 3, 4).plot(self.year_quarter_list, self.percentile_median_list, color = 'blue', linewidth = 2, label = 'Median')
        plt.subplot(2, 3, 4).plot(self.year_quarter_list, self.percentile_75th_list, color = 'green', linewidth = 2, linestyle = 'dashed', label = '75th Percentile')
        plt.subplot(2, 3, 4).set_title('Comparison', loc = 'left')
        plt.subplot(2, 3, 4).legend(loc = 'upper right')

        plt.subplot(2, 3, 5).plot(self.year_quarter_list, list(np.subtract(self.percentile_75th_list, self.percentile_25th_list)), color = 'purple', linewidth = 2, linestyle = 'dotted')
        plt.subplot(2, 3, 5).set_title('IQR', loc = 'left')

        plt.subplot(2, 3, 6).plot(self.year_quarter_list, [i / j for i, j in zip(list(np.subtract(self.percentile_75th_list, self.percentile_25th_list)), self.percentile_25th_list)], color = 'pink', linewidth = 2, linestyle = 'dotted')
        plt.subplot(2, 3, 6).set_title('IQR (weighted)', loc = 'left')

        for i in range(1, 7):
            plt.subplot(2, 3, i).set_xlabel('YEAR-QUARTER', fontsize = 9)
            plt.subplot(2, 3, i).xaxis.labelpad = 10
            plt.subplot(2, 3, i).set_ylabel(statistic_in_words, fontsize = 9)
            plt.subplot(2, 3, i).set_xticks(self.year_quarter_list[::16])
            plt.subplot(2, 3, i).set_xticklabels(self.year_quarter_list[::16], rotation = 45)
            plt.subplot(2, 3, i).yaxis.set_major_locator(MaxNLocator(nbins = 6, integer = True))

        plt.show()

try:
    os.system('cls' if os.name == 'nt' else 'clear')
    # RGDP
    Plot('spf_plot_data/Individual_RGDP.xlsx', 'RGDP', 'RGDP', False, False)
    # RGDP Growth
    Plot('spf_plot_data/Individual_RGDP.xlsx', 'RGDP', 'RGDP', True, False)
    # PRGDP
    Plot('spf_plot_data/Individual_PRGDP.xlsx', 'PRGDP', 'Probability of RGDP Change', False, False)
    # CPI
    Plot('spf_plot_data/Individual_CPI.xlsx', 'CPI', 'CPI', False, False)
    # CORECPI
    Plot('spf_plot_data/Individual_CORECPI.xlsx', 'CORECPI', 'CORECPI', False, False)
    # PCE
    Plot('spf_plot_data/Individual_PCE.xlsx', 'PCE', 'PCE', False, False)
    # COREPCE
    Plot('spf_plot_data/Individual_COREPCE.xlsx', 'COREPCE', 'COREPCE', False, False)
    # RR1_TBILL_PGDP
    Plot('spf_plot_data/Individual_RR1_TBILL_PGDP.xlsx', 'RR1_TBILL_PGDP', 'Deflated 3-Month Treasury Bill', False, True)
    # SPR_TBOND_TBILL
    Plot('spf_plot_data/Individual_SPR_TBOND_TBILL.xlsx', 'SPR_Tbond_Tbill', '10-Year Treasury Bond Yield Spread', False, False)
except:
    pass