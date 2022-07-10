import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import matplotlib.gridspec as gridspec
import warnings

class Plot:

    def __init__(self, relative_file_path, statistic, statistic_in_words, is_growth):

        self.df3 = pd.read_excel(relative_file_path).dropna(subset = [statistic + '3'])
        if is_growth:
            self.df2 = pd.read_excel(relative_file_path)

        self.year_list = self.df3.YEAR.unique()
        self.quarter_list = [1, 2, 3, 4]
        self.year_to_quarter_to_statistic = {}
        self.year_quarter_list = []
        self.percentile_25th_list = []
        self.percentile_median_list = []
        self.percentile_75th_list = []

        self.data(statistic, is_growth)
        if (is_growth):
            self.plot(statistic_in_words + ' Annualized Growth')
        else:
            self.plot(statistic_in_words)

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
                        statistics_list.append(np.percentile(self.year_to_quarter_to_statistic[year][quarter], 25, method = 'midpoint'))
                        statistics_list.append(np.percentile(self.year_to_quarter_to_statistic[year][quarter], 50, method = 'midpoint'))
                        statistics_list.append(np.percentile(self.year_to_quarter_to_statistic[year][quarter], 75, method = 'midpoint'))
                    self.year_to_quarter_to_statistic[year][quarter] = statistics_list
        else:
            previous_year_to_quarter_to_statistic = {}
            for year in self.year_list:
                if year not in previous_year_to_quarter_to_statistic:
                    previous_year_to_quarter_to_statistic[year] = {}
                # get data of current quarter
                for quarter in self.quarter_list:
                    if quarter not in previous_year_to_quarter_to_statistic[year]:
                        previous_year_to_quarter_to_statistic[year][quarter] = self.df2.loc[self.df2['YEAR'].eq(year) & self.df2['QUARTER'].eq(quarter)][statistic + '2'].fillna('').tolist()

            for year in self.year_to_quarter_to_statistic:
                for quarter in self.year_to_quarter_to_statistic[year]:
                    statistics_list = []
                    if len(self.year_to_quarter_to_statistic[year][quarter]) > 0 and len(previous_year_to_quarter_to_statistic[year][quarter]) > 0:
                        # 100 * [(current/previous)^4 - 1]
                        growth_expectation_list = []
                        for i in range(len(self.year_to_quarter_to_statistic[year][quarter])):
                            try:
                                growth_expectation_list.append(100 * ((self.year_to_quarter_to_statistic[year][quarter][i]/previous_year_to_quarter_to_statistic[year][quarter][i]) ** 4 - 1))
                            except TypeError:
                                continue

                        statistics_list.append(np.percentile(growth_expectation_list, 25, method = 'midpoint'))
                        statistics_list.append(np.percentile(growth_expectation_list, 50, method = 'midpoint'))
                        statistics_list.append(np.percentile(growth_expectation_list, 75, method = 'midpoint'))

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

    def plot(self, statistic_in_words):

        # NOTE: dark mode: plt.style.use("dark_background")
        plt.rcParams["figure.figsize"] = [13, 6.5]
        plt.rcParams["figure.autolayout"] = True
        plt.gcf().canvas.manager.set_window_title(statistic_in_words)
        plt.suptitle(statistic_in_words + ' Expectations One Quarter Ahead Plots', fontweight = 'bold', backgroundcolor = 'silver')
        plt.tight_layout()

        gs = gridspec.GridSpec(2, 6)
        plot_25 = plt.subplot(gs[0, 0:2])
        plot_median = plt.subplot(gs[0, 2:4])
        plot_75 = plt.subplot(gs[0, 4:6])
        plot_comparison = plt.subplot(gs[1, 1:3])
        plot_IQR = plt.subplot(gs[1, 3:5])

        plot_list = [plot_25, plot_median, plot_75, plot_comparison, plot_IQR]

        plot_25.plot(self.year_quarter_list, self.percentile_25th_list, color = 'red', linewidth = 2, linestyle = 'dashed')
        plot_25.set_title('25th Percentile', loc = 'left')

        plot_median.plot(self.year_quarter_list, self.percentile_median_list, color = 'blue', linewidth = 2)
        plot_median.set_title('Median', loc = 'left')

        plot_75.plot(self.year_quarter_list, self.percentile_75th_list, color = 'green', linewidth = 2, linestyle = 'dashed')
        plot_75.set_title('75th Percentile', loc = 'left')

        plot_comparison.plot(self.year_quarter_list, self.percentile_25th_list, color = 'red', linewidth = 2, linestyle = 'dashed', label = '25th Percentile')
        plot_comparison.plot(self.year_quarter_list, self.percentile_median_list, color = 'blue', linewidth = 2, label = 'Median')
        plot_comparison.plot(self.year_quarter_list, self.percentile_75th_list, color = 'green', linewidth = 2, linestyle = 'dashed', label = '75th Percentile')
        plot_comparison.set_title('Comparison', loc = 'left')

        plot_IQR.plot(self.year_quarter_list, list(np.subtract(self.percentile_75th_list, self.percentile_25th_list)), color = 'purple', linewidth = 2, linestyle = 'dotted')
        plot_IQR.set_title('IQR', loc = 'left')

        for plot in plot_list:
            plot.set_xlabel('YEAR-QUARTER', fontsize = 9)
            plot.set_ylabel(statistic_in_words, fontsize = 9)
            plot.xaxis.labelpad = 10
            plot.yaxis.set_major_locator(MaxNLocator(nbins = 6, integer = True))
            plot.set_xticks(self.year_quarter_list[::16])
            plot.set_xticklabels(self.year_quarter_list[::16], rotation = 45)
            plot.grid()

        plt.savefig('/Users/franksi-unchiu/Desktop/Handlan Summer Research 2022/Plots/spf_' + statistic_in_words + '.png', dpi = 1000)
        plt.show()

os.system('cls' if os.name == 'nt' else 'clear')
warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')
# RGDP
Plot('spf_plot_data/Individual_RGDP.xlsx', 'RGDP', 'RGDP', False)
# RGDP Growth
Plot('spf_plot_data/Individual_RGDP.xlsx', 'RGDP', 'RGDP', True)
# PRGDP
Plot('spf_plot_data/Individual_PRGDP.xlsx', 'PRGDP', 'Probability of RGDP Change', False)
# CPI
Plot('spf_plot_data/Individual_CPI.xlsx', 'CPI', 'CPI', False)
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