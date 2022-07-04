import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import math
import copy
import warnings

class Survey:

    def __init__(self, SCE_relative_file_path, SCE_spreadsheet, SCE_column, UMSC_relative_file_path, UMSC_column, SPF_relative_file_path, SPF_column, livingston_relative_file_path, livingston_spreadsheet, livingston_column, FOMC_relative_file_path, FOMC_spreadsheet, FOMC_column, variable, y_label):

        plt.rcParams["figure.figsize"] = [12, 6]
        plt.rcParams["figure.autolayout"] = True
        plt.gcf().canvas.manager.set_window_title('Survey')

        list_to_use_for_xtick_list = []
        if FOMC_relative_file_path is not None:
            self.FOMC(FOMC_relative_file_path, FOMC_spreadsheet, FOMC_column)
            list_to_use_for_xtick_list.append(self.FOMC_year_month_list)
        if livingston_relative_file_path is not None:
            self.livingston(livingston_relative_file_path, livingston_spreadsheet, livingston_column)
            list_to_use_for_xtick_list.append(self.livingston_year_month_list)
        if SPF_relative_file_path is not None:
            self.SPF(SPF_relative_file_path, SPF_column)
            list_to_use_for_xtick_list.append(self.SPF_year_month_list)
        if UMSC_relative_file_path is not None: 
            self.UMSC(UMSC_relative_file_path, UMSC_column)
            list_to_use_for_xtick_list.append(self.UMSC_year_month_list)
        if SCE_relative_file_path is not None: 
            self.SCE(SCE_relative_file_path, SCE_spreadsheet, SCE_column)
            list_to_use_for_xtick_list.append(self.SCE_year_month_list)

        plt.title(variable + ' Survey Data', fontweight = 'bold', backgroundcolor = 'silver')
        plt.xlabel('YEAR_MONTH', labelpad = 10)
        plt.ylabel(y_label, labelpad = 10)

        min = list_to_use_for_xtick_list[0][0]
        list_to_use = list_to_use_for_xtick_list[0]
        for list in list_to_use_for_xtick_list:
            if list[0] < min:
                min = list[0]
                list_to_use = list
        xtick_list = list_to_use

        temp_xtick_list = []
        for xtick in xtick_list:
            frac, whole = math.modf(xtick)
            temp_xtick_list.append(str(int(whole)) + '-' + str(int(frac * 12 + 0.1)))

        plt.xticks(xtick_list[::16])
        xtick_list = temp_xtick_list
        plt.gca().set_xticklabels(xtick_list[::16], rotation = 45)
        plt.legend(loc = 'upper right')
        plt.grid()

        plt.show()

    def SCE(self, SCE_relative_file_path, SCE_spreadsheet, SCE_column):
        SCE_excel = pd.ExcelFile(SCE_relative_file_path)
        SCE_df = pd.read_excel(SCE_excel, SCE_spreadsheet, skiprows=[0, 1, 2])
        self.SCE_year_month_list = SCE_df.iloc[:, [0]].values.tolist()
        self.SCE_statistic_list = SCE_df.loc[:, SCE_column].tolist()

        for i in range(len(self.SCE_year_month_list)):
            year_month = str(self.SCE_year_month_list[i][0])[:4] + '-' + str(self.SCE_year_month_list[i][0])[4:]
            year_month = year_month.split('-')
            year_month = int(year_month[0]) + int(year_month[1])/12
            self.SCE_year_month_list[i] = year_month

        plt.plot(self.SCE_year_month_list, self.SCE_statistic_list, color = 'pink', linewidth = 2, label = 'Survey of Consumer Expectations')

    def UMSC(self, UMSC_relative_file_path, UMSC_column):
        UMSC_df = pd.read_excel(UMSC_relative_file_path, usecols = ['Month', 'yyyy', UMSC_column], skiprows = [0])
        UMSC_year_list = UMSC_df.yyyy.unique()
        UMSC_month_list = UMSC_df.Month.unique()

        UMSC_year_to_month_to_statistic = {}
        for year in UMSC_year_list:
            if year not in UMSC_year_to_month_to_statistic:
                UMSC_year_to_month_to_statistic[year] = {}
            for month in UMSC_month_list:
                if month not in UMSC_year_to_month_to_statistic[year]:
                    array = None
                    if UMSC_df.loc[UMSC_df['yyyy'].eq(year) & UMSC_df['Month'].eq(month)].size != 0:
                        array = UMSC_df.loc[UMSC_df['yyyy'].eq(year) & UMSC_df['Month'].eq(month)].values[-1][2]
                    UMSC_year_to_month_to_statistic[year][month] = array

        UMSC_year_month_to_statistic = {}
        for year in UMSC_year_to_month_to_statistic:
            for temp_month in UMSC_year_to_month_to_statistic[year]:
                if len(str(temp_month)) < 2:
                    month = '0' + str(temp_month)
                else:
                    month = str(temp_month)
                year_month = int(year) + int(month)/12
                if year_month not in UMSC_year_month_to_statistic:
                    UMSC_year_month_to_statistic[year_month] = UMSC_year_to_month_to_statistic[year][temp_month]

        for year_month, statistic in copy.deepcopy(UMSC_year_month_to_statistic).items():
            if statistic == None:
                del UMSC_year_month_to_statistic[year_month]

        self.UMSC_year_month_list = []
        self.UMSC_statistic_list = []
        for year_month, statistic in UMSC_year_month_to_statistic.items():
            self.UMSC_year_month_list.append(year_month)
            self.UMSC_statistic_list.append(statistic)

        plt.plot(self.UMSC_year_month_list, self.UMSC_statistic_list, color = 'purple', linewidth = 2, label = 'University of Michigan Survey of Consumers')

    def SPF(self, SPF_relative_file_path, SPF_column):
        SPF_df = pd.read_excel(SPF_relative_file_path).dropna(subset = SPF_column)
        SPF_year_list = SPF_df.YEAR.unique()
        SPF_quarter_list = [1, 2, 3, 4]
        SPF_year_to_quarter_to_statistic = {}
        self.SPF_year_month_list = []
        self.SPF_statistic_list = []

        for year in SPF_year_list:
            if year not in SPF_year_to_quarter_to_statistic:
                SPF_year_to_quarter_to_statistic[year] = {}
            for quarter in SPF_quarter_list:
                if quarter not in SPF_year_to_quarter_to_statistic[year]:
                    SPF_year_to_quarter_to_statistic[year][quarter] = SPF_df.loc[SPF_df['YEAR'].eq(year) & SPF_df['QUARTER'].eq(quarter)][SPF_column].tolist()

        for year in SPF_year_to_quarter_to_statistic:
            for quarter in SPF_year_to_quarter_to_statistic[year]:
                statistics_list = []
                if len(SPF_year_to_quarter_to_statistic[year][quarter]) > 0:
                    statistics_list = [np.percentile(SPF_year_to_quarter_to_statistic[year][quarter], 50, method = 'midpoint')]
                SPF_year_to_quarter_to_statistic[year][quarter] = statistics_list

        SPF_year_month_to_statistic = {}
        for year in SPF_year_to_quarter_to_statistic:
            for quarter in SPF_year_to_quarter_to_statistic[year]:
                if quarter == 1:
                    month = '01'
                elif quarter == 2:
                    month = '04'
                elif quarter == 3:
                    month = '07'
                elif quarter == 4:
                    month = '10'
                year_month = int(year) + int(month)/12
                if year_month not in SPF_year_month_to_statistic:
                    if len(SPF_year_to_quarter_to_statistic[year][quarter]) > 0:
                        SPF_year_month_to_statistic[year_month] = SPF_year_to_quarter_to_statistic[year][quarter]

        self.SPF_year_month_list = []
        self.SPF_statistic_list = []
        for year_month, statistic in SPF_year_month_to_statistic.items():
            self.SPF_year_month_list.append(year_month)
            self.SPF_statistic_list.append(statistic)

        plt.plot(self.SPF_year_month_list, self.SPF_statistic_list, color = 'green', linewidth = 2, label = 'Survey of Professional Forecasters')

    def livingston(self, livingston_relative_file_path, livingston_spreadsheet, livingston_column):
        livingston_excel = pd.ExcelFile(livingston_relative_file_path)
        livingston_df = pd.read_excel(livingston_excel, livingston_spreadsheet).dropna(subset = [livingston_column])
        self.livingston_year_month_list = livingston_df['Date'].to_list()
        self.livingston_statistic_list = livingston_df.loc[:, livingston_column].tolist()

        self.livingston_year_month_list = [datetime.strptime(str(x), '%Y-%m-%d %H:%M:%S') for x in self.livingston_year_month_list]
        self.livingston_year_month_list = [int(x.year) + int(x.month)/12 for x in self.livingston_year_month_list]

        if livingston_spreadsheet == 'CPI':
            self.livingston_statistic_list = [(int(x) - 100)/10 for x in self.livingston_statistic_list if x is not None]

        plt.plot(self.livingston_year_month_list, self.livingston_statistic_list, color = 'blue', linewidth = 2, label = 'Livingston Survey')

    def FOMC(self, FOMC_relative_file_path, FOMC_spreadsheet, FOMC_column):
        FOMC_excel = pd.ExcelFile(FOMC_relative_file_path)
        FOMC_df = pd.read_excel(FOMC_excel, FOMC_spreadsheet).dropna(subset = FOMC_column)
        self.FOMC_year_month_list = FOMC_df['DATE'].values.tolist()
        self.FOMC_statistic_list = FOMC_df.loc[:, FOMC_column].tolist()

        temp_FOMC_year_month_list = []
        for year_month in self.FOMC_year_month_list:
            frac, whole = math.modf(year_month)
            frac = int(frac * 10 + 0.1)
            if frac == 2:
                frac = 4
            elif frac == 3:
                frac = 7
            elif frac == 4:
                frac = 10
            temp_FOMC_year_month_list.append(whole + frac/12)
        self.FOMC_year_month_list = temp_FOMC_year_month_list

        plt.plot(self.FOMC_year_month_list, self.FOMC_statistic_list, color = 'red', linewidth = 2, label = 'Tealbook Dataset')

warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')

# inflation
Survey('survey_data/FRBNY-SCE-Data.xlsx', 'Inflation expectations', 'Median one-year ahead expected inflation rate', 'survey_data/sca-tableall-on-2022-Jul-02.xls', 'px1_med_all', 'spf_plot_data/Individual_CPI.xlsx', 'CPI6', 'survey_data/medians.xlsx', 'CPI', 'CPI_12M', 'GBweb_Row_Format.xlsx', 'gPCPI', 'gPCPIF4', 'Inflation', 'EXPECTED INFLATION RATE ONE YEAR AHEAD') # TODO: livingston is CPI

# RGDP
Survey('survey_data/FRBNY-SCE-Data.xlsx', 'Earnings growth', 'Median expected earnings growth', 'survey_data/sca-tableall-on-2022-Jul-02.xls', 'inex_med_all', None, None, None, None, None, None, None, None, 'RGDP', 'EXPECTED EARNING/INCOME GROWTH RATE ONE YEAR AHEAD') # Tealbook is growth
Survey(None, None, None, None, None, 'spf_plot_data/Individual_RGDP.xlsx', 'RGDP6', 'survey_data/medians.xlsx', 'RGDPX', 'RGDPX_12M', 'GBweb_Row_Format.xlsx', 'gRGDP', 'gRGDPF4', 'RGDP', 'EXPECTED RGDP ONE YEAR AHEAD')

# unemployment
Survey('survey_data/FRBNY-SCE-Data.xlsx', 'Unemployment Expectations', 'Mean probability that the U.S. unemployment rate will be higher one year from now', 'survey_data/sca-tableall-on-2022-Jul-02.xls', 'umex_u_all', 'survey_data/Individual_PRUNEMP.xlsx', 'PRUNEMP6', None, None, None, None, None, None, 'Unemployment Rate', 'PROBABILITY US UNEMPLOYMENT RATE WILL BE HIGHER NEXT YEAR') # TODO: is this right?
Survey(None, None, None, None, None, 'survey_data/Individual_UNEMP.xlsx', 'UNEMP6', 'survey_data/medians.xlsx', 'UNPR', 'UNPR_12M', 'GBweb_Row_Format.xlsx', 'UNEMP', 'UNEMPF4', 'Unemployment Rate', 'EXPECTED UNEMPLOYMENT RATE ONE YEAR AHEAD')

# interest rate
Survey('survey_data/FRBNY-SCE-Data.xlsx', 'Interest rate expectations', 'Mean probability of higher average interest rate on savings accounts one year from now', 'survey_data/sca-tableall-on-2022-Jul-02.xls', 'ratex_u_all', None, None, None, None, None, None, None, None, 'Interest Rate', 'PROBABILITY OF HIGHER INTEREST RATE NEXT YEAR')
Survey(None, None, None, None, None, 'spf_plot_data/Individual_RR1_TBILL_PGDP.xlsx', 'RR1_TBILL_PGDP_3', 'survey_data/medians.xlsx', 'TBILL', 'TBILL_12M', None, None, None, 'Interest Rate', 'EXPECTED INTEREST RATE ONE QUARTER AHEAD')

# https://data.sca.isr.umich.edu/subset/codebook.php
# for UMSC: instead of doing probability, I did the number of people who said it'll go higher