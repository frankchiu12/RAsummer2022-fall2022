import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class Plot:

    def __init__(self, file_path, statistic):
        self.df = pd.read_excel(file_path).dropna(subset=[statistic + '1'])
        self.year_list = self.df.YEAR.unique()
        self.quarter_list = [1, 2, 3, 4]
        self.year_to_quarter_to_statistics = {}
        self.year_quarter_list = []
        self.percentile_25th_list = []
        self.percentile_median_list = []
        self.percentile_75th_list = []
        self.data(statistic)
        self.plot(statistic)

    def data(self, statistic):
        for year in self.year_list:
            if year not in self.year_to_quarter_to_statistics:
                self.year_to_quarter_to_statistics[year] = {}
            for quarter in self.quarter_list:
                if quarter not in self.year_to_quarter_to_statistics[year]:
                    self.year_to_quarter_to_statistics[year][quarter] = self.df.loc[self.df['YEAR'].eq(year) & self.df['QUARTER'].eq(quarter)][statistic + '1'].tolist()

        for year in self.year_to_quarter_to_statistics:
            for quarter in self.year_to_quarter_to_statistics[year]:
                statistics_list = []
                if len(self.year_to_quarter_to_statistics[year][quarter]) > 0:
                    statistics_list.append(np.percentile(self.year_to_quarter_to_statistics[year][quarter], 25))
                    statistics_list.append(np.percentile(self.year_to_quarter_to_statistics[year][quarter], 50))
                    statistics_list.append(np.percentile(self.year_to_quarter_to_statistics[year][quarter], 75))
                self.year_to_quarter_to_statistics[year][quarter] = statistics_list

        year_quarter_to_statistics = {}
        for year in self.year_to_quarter_to_statistics:
            for quarter in self.year_to_quarter_to_statistics[year]:
                if str(int(year)) + '-' + str(quarter) not in year_quarter_to_statistics:
                    if len(self.year_to_quarter_to_statistics[year][quarter]) > 0:
                        year_quarter_to_statistics[str(int(year)) + '-' + str(quarter)] = self.year_to_quarter_to_statistics[year][quarter]

        for year_quarter, statistic in year_quarter_to_statistics.items():
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

        for i in range(1, 4):
            plt.subplot(2, 2, i)
            plt.tight_layout()

        plt.subplot(2, 2, 1).plot(self.year_quarter_list, self.percentile_25th_list, color = 'blue', linewidth = 3)
        plt.subplot(2, 2, 1).set_title('25th Percentile ' + statistic, loc='left')
        plt.subplot(2, 2, 2).plot(self.year_quarter_list, self.percentile_median_list, color = 'red', linewidth = 3)
        plt.subplot(2, 2, 2).set_title('Median ' + statistic, loc='left')
        plt.subplot(2, 2, 3).plot(self.year_quarter_list, self.percentile_75th_list, color = 'green', linewidth = 3)
        plt.subplot(2, 2, 3).set_title('75th Percentile ' + statistic, loc='left')

        for i in range(1, 4):
            plt.subplot(2, 2, i).set_xlabel('YEAR-QUARTER')
            plt.subplot(2, 2, i).xaxis.labelpad = 10
            plt.subplot(2, 2, i).set_ylabel(statistic)
            plt.subplot(2, 2, i).set_xticks(self.year_quarter_list[::16])
            plt.subplot(2, 2, i).set_xticklabels(self.year_quarter_list[::16], rotation=45)

        plt.show()

# RGDP
# Plot('/Users/franksi-unchiu/Downloads/Individual_RGDP.xlsx', 'RGDP')
# CPI
# Plot('/Users/franksi-unchiu/Downloads/Individual_CPI.xlsx', 'CPI')
# PCE
Plot('/Users/franksi-unchiu/Downloads/Individual_PCE.xlsx', 'PCE')

# QUESTIONS:
# 1. any visual changes?
# 2. which data do I continue with?
# 3. overlap doesn't help
