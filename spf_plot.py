import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np

class Plot:

    def __init__(self, relative_file_path, statistic, statistic_in_words, is_growth):

        self.df3 = pd.read_excel(relative_file_path).dropna(subset=[statistic + '3'])
        if is_growth:
            self.df2 = pd.read_excel(relative_file_path).dropna(subset=[statistic + '2'])

        self.year_list = self.df3.YEAR.unique()
        self.quarter_list = [1, 2, 3, 4]
        self.year_to_quarter_to_statistic = {}
        self.year_quarter_list = []
        self.percentile_25th_list = []
        self.percentile_median_list = []
        self.percentile_75th_list = []

        self.data(statistic, is_growth)
        if (is_growth):
            self.plot(statistic, statistic_in_words + ' Annualized Growth', is_growth)
        else:
            self.plot(statistic, statistic_in_words, is_growth)

    def data(self, statistic, is_growth):
        # get data of one quarter ahead
        for year in self.year_list:
            if year not in self.year_to_quarter_to_statistic:
                self.year_to_quarter_to_statistic[year] = {}
            for quarter in self.quarter_list:
                if quarter not in self.year_to_quarter_to_statistic[year]:
                    self.year_to_quarter_to_statistic[year][quarter] = self.df3.loc[self.df3['YEAR'].eq(year) & self.df3['QUARTER'].eq(quarter)][statistic + '3'].tolist()

        if (not is_growth):
            for year in self.year_to_quarter_to_statistic:
                for quarter in self.year_to_quarter_to_statistic[year]:
                    statistics_list = []
                    if len(self.year_to_quarter_to_statistic[year][quarter]) > 0:
                        statistics_list.append(np.percentile(self.year_to_quarter_to_statistic[year][quarter], 25))
                        statistics_list.append(np.percentile(self.year_to_quarter_to_statistic[year][quarter], 50))
                        statistics_list.append(np.percentile(self.year_to_quarter_to_statistic[year][quarter], 75))
                    self.year_to_quarter_to_statistic[year][quarter] = statistics_list
        else:
            previous_year_to_quarter_to_statistic = {}

            for year in self.year_list:
                if year not in previous_year_to_quarter_to_statistic:
                    previous_year_to_quarter_to_statistic[year] = {}
                # get data of current quarter
                for quarter in self.quarter_list:
                    if quarter not in previous_year_to_quarter_to_statistic[year]:
                        previous_year_to_quarter_to_statistic[year][quarter] = self.df2.loc[self.df2['YEAR'].eq(year) & self.df2['QUARTER'].eq(quarter)][statistic + '2'].tolist()

            for year in self.year_to_quarter_to_statistic:
                for quarter in self.year_to_quarter_to_statistic[year]:
                    statistics_list = []
                    if len(self.year_to_quarter_to_statistic[year][quarter]) > 0 and len(previous_year_to_quarter_to_statistic[year][quarter]) > 0:
                        # 100 * [(current/previous)^4 - 1]
                        statistics_list.append(100 * ((np.percentile(self.year_to_quarter_to_statistic[year][quarter], 25)/np.percentile(previous_year_to_quarter_to_statistic[year][quarter], 25)) ** 4 - 1))
                        statistics_list.append(100 * ((np.percentile(self.year_to_quarter_to_statistic[year][quarter], 50)/np.percentile(previous_year_to_quarter_to_statistic[year][quarter], 50)) ** 4 - 1))
                        statistics_list.append(100 * ((np.percentile(self.year_to_quarter_to_statistic[year][quarter], 75)/np.percentile(previous_year_to_quarter_to_statistic[year][quarter], 75)) ** 4 - 1))
                    
                        print(str(year) + ' + ' + str(quarter))
                        print(np.percentile(self.year_to_quarter_to_statistic[year][quarter], 50))
                        print(np.percentile(previous_year_to_quarter_to_statistic[year][quarter], 50))
                        print(100 * ((np.percentile(self.year_to_quarter_to_statistic[year][quarter], 50)/np.percentile(previous_year_to_quarter_to_statistic[year][quarter], 50)) ** 4 - 1))

                    self.year_to_quarter_to_statistic[year][quarter] = statistics_list

        # convert {1968:{4:statistic}} to {1968-4:statistic}
        year_quarter_to_statistic = {}
        for year in self.year_to_quarter_to_statistic:
            for quarter in self.year_to_quarter_to_statistic[year]:
                if str(int(year)) + '-' + str(quarter) not in year_quarter_to_statistic:
                    if len(self.year_to_quarter_to_statistic[year][quarter]) > 0:
                        year_quarter_to_statistic[str(int(year)) + '-' + str(quarter)] = self.year_to_quarter_to_statistic[year][quarter]

        for year_quarter, statistic in year_quarter_to_statistic.items():
            self.year_quarter_list.append(year_quarter)
            self.percentile_25th_list.append(statistic[0])
            self.percentile_median_list.append(statistic[1])
            self.percentile_75th_list.append(statistic[2])

    def plot(self, statistic, statistic_in_words, is_growth):

        # NOTE: dark mode: plt.style.use("dark_background")
        plt.rcParams["figure.figsize"] = [13, 6.5]
        plt.rcParams["figure.autolayout"] = True
        plt.gcf().canvas.manager.set_window_title(statistic_in_words)
        plt.suptitle(statistic_in_words + ' Expectations One Quarter Ahead Plots', fontweight = 'bold', backgroundcolor = 'silver')

        for i in range(1, 7):
            plt.subplot(2, 3, i)
            plt.tight_layout()
            plt.labelsize = 10

        # 25th percentile
        plt.subplot(2, 3, 1).plot(self.year_quarter_list, self.percentile_25th_list, color = 'red', linewidth = 2, linestyle = 'dashed')
        if is_growth:
            plt.subplot(2, 3, 1).set_title('25th Percentile', loc = 'right')
        else:
            plt.subplot(2, 3, 1).set_title('25th Percentile', loc = 'left')
        # median
        plt.subplot(2, 3, 2).plot(self.year_quarter_list, self.percentile_median_list, color = 'blue', linewidth = 2)
        if is_growth:
            plt.subplot(2, 3, 2).set_title('Median', loc = 'right')
        else:
            plt.subplot(2, 3, 2).set_title('Median', loc = 'left')
        # 75th percentile
        plt.subplot(2, 3, 3).plot(self.year_quarter_list, self.percentile_75th_list, color = 'green', linewidth = 2, linestyle = 'dashed')
        if is_growth:
            plt.subplot(2, 3, 3).set_title('75th Percentile', loc = 'right')
        else:
            plt.subplot(2, 3, 3).set_title('75th Percentile', loc = 'left')
        # all of them
        plt.subplot(2, 3, 4).plot(self.year_quarter_list, self.percentile_25th_list, color = 'red', linewidth = 2, linestyle = 'dashed', label = '25th Percentile')
        plt.subplot(2, 3, 4).plot(self.year_quarter_list, self.percentile_median_list, color = 'blue', linewidth = 2, label = 'Median')
        plt.subplot(2, 3, 4).plot(self.year_quarter_list, self.percentile_75th_list, color = 'green', linewidth = 2, linestyle = 'dashed', label = '75th Percentile')
        if is_growth:
            plt.subplot(2, 3, 4).set_title('Comparison', loc = 'right')
        else:
            plt.subplot(2, 3, 4).set_title('Comparison', loc = 'left')
        plt.subplot(2, 3, 4).legend(loc = 'upper right')
        # IQR
        plt.subplot(2, 3, 5).plot(self.year_quarter_list, list(np.subtract(self.percentile_75th_list, self.percentile_25th_list)), color = 'purple', linewidth = 2, linestyle = 'dotted')
        if is_growth:
            plt.subplot(2, 3, 5).set_title('IQR', loc = 'right')
        else:
            plt.subplot(2, 3, 5).set_title('IQR', loc = 'left')
        # IQR (weighted)
        plt.subplot(2, 3, 6).plot(self.year_quarter_list, [i / j for i, j in zip(list(np.subtract(self.percentile_75th_list, self.percentile_25th_list)), self.percentile_25th_list)], color = 'pink', linewidth = 2, linestyle = 'dotted')
        if is_growth:
            plt.subplot(2, 3, 6).set_title('IQR (weighted)', loc = 'right')
        else:
            plt.subplot(2, 3, 6).set_title('IQR (weighted)', loc = 'left')

        for i in range(1, 7):
            plt.subplot(2, 3, i).set_xlabel('YEAR-QUARTER', fontsize = 9)
            plt.subplot(2, 3, i).set_ylabel(statistic_in_words, fontsize = 9)
            plt.subplot(2, 3, i).xaxis.labelpad = 10
            plt.subplot(2, 3, i).yaxis.set_major_locator(MaxNLocator(nbins = 6, integer = True))
            plt.subplot(2, 3, i).set_xticks(self.year_quarter_list[::16])
            plt.subplot(2, 3, i).set_xticklabels(self.year_quarter_list[::16], rotation = 45)

        plt.show()

try:
    os.system('cls' if os.name == 'nt' else 'clear')
    # RGDP
    Plot('spf_plot_data/Individual_RGDP.xlsx', 'RGDP', 'RGDP', False)
    # RGDP Growth
    Plot('spf_plot_data/Individual_RGDP.xlsx', 'RGDP', 'RGDP', True)
    # PRGDP
    Plot('spf_plot_data/Individual_PRGDP.xlsx', 'PRGDP', 'Probability of RGDP Change', False)
    # CPI
    Plot('spf_plot_data/Individual_CPI.xlsx', 'CPI', 'CPI', False)
    # CPI Growth
    Plot('spf_plot_data/Individual_CPI.xlsx', 'CPI', 'CPI', True)
    # CORECPI
    Plot('spf_plot_data/Individual_CORECPI.xlsx', 'CORECPI', 'CORECPI', False)
    # PCE
    Plot('spf_plot_data/Individual_PCE.xlsx', 'PCE', 'PCE', False)
    # COREPCE
    Plot('spf_plot_data/Individual_COREPCE.xlsx', 'COREPCE', 'COREPCE', False)
    # RR1_TBILL_PGDP
    Plot('spf_plot_data/Individual_RR1_TBILL_PGDP.xlsx', 'RR1_TBILL_PGDP_', 'Deflated 3-Month Treasury Bill', False)
    # SPR_TBOND_TBILL
    Plot('spf_plot_data/Individual_SPR_TBOND_TBILL.xlsx', 'SPR_Tbond_Tbill', '10-Year Treasury Bond Yield Spread', False)
except:
    pass