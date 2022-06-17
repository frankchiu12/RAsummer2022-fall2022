import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class Plot:

    def __init__(self, relative_file_path, statistic):

        self.df = pd.read_excel(relative_file_path).dropna(subset=[statistic + '3'])
        self.year_list = self.df.YEAR.unique()
        self.quarter_list = [1, 2, 3, 4]
        self.year_to_quarter_to_statistic = {}
        self.year_quarter_list = []
        self.percentile_25th_list = []
        self.percentile_median_list = []
        self.percentile_75th_list = []
        self.data(statistic)
        self.plot(statistic)

    def data(self, statistic):

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

        for year_quarter, statistic in year_quarter_to_statistic.items():
            self.year_quarter_list.append(year_quarter)
            self.percentile_25th_list.append(statistic[0])
            self.percentile_median_list.append(statistic[1])
            self.percentile_75th_list.append(statistic[2])

    def plot(self, statistic):

        # NOTE: dark mode: plt.style.use("dark_background")
        plt.rcParams["figure.figsize"] = [12, 6]
        plt.rcParams["figure.autolayout"] = True
        plt.gcf().canvas.manager.set_window_title(statistic)
        plt.suptitle(statistic, fontweight = 'bold', backgroundcolor = 'silver')

        for i in range(1, 5):
            plt.subplot(2, 2, i)
            plt.tight_layout()

        plt.subplot(2, 2, 1).plot(self.year_quarter_list, self.percentile_25th_list, color = 'red', linewidth = 2)
        plt.subplot(2, 2, 1).set_title('25th Percentile ' + statistic, loc = 'left')
        plt.subplot(2, 2, 2).plot(self.year_quarter_list, self.percentile_median_list, color = 'blue', linewidth = 2)
        plt.subplot(2, 2, 2).set_title('Median ' + statistic, loc = 'left')
        plt.subplot(2, 2, 3).plot(self.year_quarter_list, self.percentile_75th_list, color = 'green', linewidth = 2)
        plt.subplot(2, 2, 3).set_title('75th Percentile ' + statistic, loc = 'left')
        plt.subplot(2, 2, 4).plot(self.year_quarter_list, self.percentile_25th_list, color = 'red', linewidth = 2)
        plt.subplot(2, 2, 4).plot(self.year_quarter_list, self.percentile_median_list, color = 'blue', linewidth = 2)
        plt.subplot(2, 2, 4).plot(self.year_quarter_list, self.percentile_75th_list, color = 'green', linewidth = 2)
        plt.subplot(2, 2, 4).set_title('Comparison of ' + statistic, loc = 'left')

        for i in range(1, 5):
            plt.subplot(2, 2, i).set_xlabel('YEAR-QUARTER')
            plt.subplot(2, 2, i).xaxis.labelpad = 10
            plt.subplot(2, 2, i).set_ylabel(statistic)
            plt.subplot(2, 2, i).set_xticks(self.year_quarter_list[::16])
            plt.subplot(2, 2, i).set_xticklabels(self.year_quarter_list[::16], rotation = 45)

        plt.show()

os.system('cls' if os.name == 'nt' else 'clear')
# RGDP
Plot('spf_plot_data/Individual_RGDP.xlsx', 'RGDP')
# CPI
Plot('spf_plot_data/Individual_CPI.xlsx', 'CPI')
# PCE
Plot('spf_plot_data/Individual_PCE.xlsx', 'PCE')