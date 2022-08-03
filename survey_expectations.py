import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import math
import copy
import warnings

class Survey:

    def __init__(self, SCE_relative_file_path, SCE_spreadsheet, SCE_column, UMSC_relative_file_path, UMSC_column, SPF_relative_file_path, SPF_column, livingston_relative_file_path, livingston_spreadsheet, livingston_column, FOMC_relative_file_path, FOMC_spreadsheet, FOMC_column, SEP_relative_file_path, SEP_column, has_long_base, variable, y_label):

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
        if SEP_relative_file_path is not None:
            self.SEP(SEP_relative_file_path, SEP_column)
            list_to_use_for_xtick_list.append(self.SEP_year_month_list)
        if has_long_base:
            self.long_base()
            list_to_use_for_xtick_list.append(self.long_base_year_month_list)

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

        plt.savefig('/Users/franksi-unchiu/Desktop/Handlan Summer Research 2022/Plots/survey_' + y_label + '.png', dpi = 1000)
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
        SPF_df1 = pd.read_excel(SPF_relative_file_path).dropna(subset = SPF_column)
        SPF_year_list = SPF_df1.YEAR.unique()
        SPF_quarter_list = [1, 2, 3, 4]
        SPF_year_to_quarter_to_statistic = {}
        self.SPF_year_month_list = []
        self.SPF_statistic_list = []

        for year in SPF_year_list:
            if year not in SPF_year_to_quarter_to_statistic:
                SPF_year_to_quarter_to_statistic[year] = {}
            for quarter in SPF_quarter_list:
                if quarter not in SPF_year_to_quarter_to_statistic[year]:
                    SPF_year_to_quarter_to_statistic[year][quarter] = SPF_df1.loc[SPF_df1['YEAR'].eq(year) & SPF_df1['QUARTER'].eq(quarter)][SPF_column].tolist()

        if SPF_column == 'NGDP6':
            SPF_df2 = pd.read_excel(SPF_relative_file_path)
            SPF_previous_year_to_quarter_to_statistic = {}
            for year in SPF_year_list:
                if year not in SPF_previous_year_to_quarter_to_statistic:
                    SPF_previous_year_to_quarter_to_statistic[year] = {}
                for quarter in SPF_quarter_list:
                    if quarter not in SPF_previous_year_to_quarter_to_statistic[year]:
                        SPF_previous_year_to_quarter_to_statistic[year][quarter] = SPF_df2.loc[SPF_df2['YEAR'].eq(year) & SPF_df2['QUARTER'].eq(quarter)]['NGDP5'].fillna('').tolist()

            for year in SPF_year_to_quarter_to_statistic:
                for quarter in SPF_year_to_quarter_to_statistic[year]:  
                    statistics_list = []
                    if len(SPF_year_to_quarter_to_statistic[year][quarter]) > 0 and len(SPF_previous_year_to_quarter_to_statistic[year][quarter]) > 0:
                        growth_expectation_list = []
                        for i in range(len(SPF_year_to_quarter_to_statistic[year][quarter])):
                            try:
                                growth_expectation_list.append(100 * ((SPF_year_to_quarter_to_statistic[year][quarter][i]/SPF_previous_year_to_quarter_to_statistic[year][quarter][i]) ** 4 - 1))
                            except TypeError:
                                continue
                        statistics_list = [np.percentile(growth_expectation_list, 50, method = 'midpoint')]
                    SPF_year_to_quarter_to_statistic[year][quarter] = statistics_list
        else:
            for year in SPF_year_to_quarter_to_statistic:
                for quarter in SPF_year_to_quarter_to_statistic[year]:
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

        if livingston_spreadsheet == 'CPI' or livingston_spreadsheet == 'GDPX':
            if livingston_spreadsheet == 'CPI':
                self.livingston_year_month_list = self.livingston_year_month_list[39:]
                self.livingston_statistic_list = self.livingston_statistic_list[39:]
                previous_livingston_statistic_list = livingston_df.loc[:, 'CPI_ZY'].tolist()[39:]
            if livingston_spreadsheet == 'GDPX':
                previous_livingston_statistic_list = livingston_df.loc[:, 'GDPX_ZY'].tolist()

            for i in range(0, len(self.livingston_statistic_list)):
                self.livingston_statistic_list[i] = (self.livingston_statistic_list[i] - previous_livingston_statistic_list[i])/previous_livingston_statistic_list[i] * 100

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

    def SEP(self, SEP_relative_file_path, SEP_column):
        SEP_df = pd.read_excel(SEP_relative_file_path, usecols = ['meetingDate', SEP_column])
        self.SEP_year_month_list = SEP_df['meetingDate'].to_list()
        self.SEP_statistic_list = SEP_df[SEP_column].to_list()
        for i in range(len(self.SEP_year_month_list)):
            if isinstance(self.SEP_year_month_list[i], datetime):
                self.SEP_year_month_list[i] = self.SEP_year_month_list[i].year + self.SEP_year_month_list[i].month/12
            else:
                self.SEP_year_month_list[i] = int(self.SEP_year_month_list[i].split('/')[2]) + int(self.SEP_year_month_list[i].split('/')[1])/12

        plt.plot(self.SEP_year_month_list, self.SEP_statistic_list, color = 'gray', linewidth = 2, label = 'SEP')

    def long_base(self):
        long_base_pd = pd.read_csv('pyfrbus_package/data/LONGBASE.TXT', usecols = ['OBS', 'ZRFF5']).dropna(subset = 'ZRFF5')
        self.long_base_year_month_list = long_base_pd['OBS'].tolist()
        self.long_base_statistic_list = long_base_pd['ZRFF5'].tolist()

        index_to_stop = None
        for i in range(len(self.long_base_year_month_list)):
            year = int(self.long_base_year_month_list[i][:4])
            month = self.long_base_year_month_list[i][4:]
            if year > 2022:
                index_to_stop = i
                break
            if month == 'Q1':
                month = 1
            elif month == 'Q2':
                month = 4
            elif month == 'Q3':
                month = 7
            elif month == 'Q4':
                month = 10
            self.long_base_year_month_list[i] = year + month/12

        self.long_base_year_month_list = [x for x in self.long_base_year_month_list if isinstance(x, float)]
        self.long_base_statistic_list = self.long_base_statistic_list[:index_to_stop]

        plt.plot(self.long_base_year_month_list, self.long_base_statistic_list, color = 'yellow', linewidth = 2, label = 'LONGBASE')

warnings.filterwarnings('ignore', category = UserWarning, module = 'openpyxl')

# inflation
Survey('survey_data/FRBNY-SCE-Data.xlsx', 'Inflation expectations', 'Median one-year ahead expected inflation rate', 'survey_data/sca-tableall-on-2022-Jul-02.xls', 'px1_med_all', 'spf_plot_data/Individual_CPI.xlsx', 'CPI6', 'survey_data/medians.xlsx', 'CPI', 'CPI_1Y', 'other_data/GBweb_Row_Format.xlsx', 'gPCPI', 'gPCPIF4','survey_data/table1.xlsx', 'PCEInflation_t0', False, 'Inflation', 'EXPECTED INFLATION RATE ONE YEAR AHEAD')

# RGDP
Survey('survey_data/FRBNY-SCE-Data.xlsx', 'Earnings growth', 'Median expected earnings growth', 'survey_data/sca-tableall-on-2022-Jul-02.xls', 'inex_med_all', None, None, None, None, None, None, None, None, None, None, False, 'NGDP', 'EXPECTED EARNING OR INCOME GROWTH RATE ONE YEAR AHEAD')
Survey(None, None, None, None, None, 'survey_data/Individual_NGDP.xlsx', 'NGDP6', 'survey_data/medians.xlsx', 'GDPX', 'GDPX_1Y', 'other_data/GBweb_Row_Format.xlsx', 'gNGDP', 'gNGDPF4', 'survey_data/table1.xlsx', 'ChangeinRealGDP_t0', False, 'NGDP', 'EXPECTED NGDP GROWTH RATE ONE YEAR AHEAD') # table1 doesn't have NGDP

# unemployment
Survey('survey_data/FRBNY-SCE-Data.xlsx', 'Unemployment Expectations', 'Mean probability that the U.S. unemployment rate will be higher one year from now', 'survey_data/sca-tableall-on-2022-Jul-02.xls', 'umex_u_all', None, None, None, None, None, None, None, None, None, None, False, 'Unemployment Rate', 'PROBABILITY US UNEMPLOYMENT RATE WILL BE HIGHER NEXT YEAR')
Survey(None, None, None, None, None, 'survey_data/Individual_UNEMP.xlsx', 'UNEMP6', 'survey_data/medians.xlsx', 'UNPR', 'UNPR_1Y', 'other_data/GBweb_Row_Format.xlsx', 'UNEMP', 'UNEMPF4', 'survey_data/table1.xlsx', 'UnemploymentRate_t0', False, 'Unemployment Rate', 'EXPECTED UNEMPLOYMENT RATE ONE YEAR AHEAD')

# interest rate
Survey('survey_data/FRBNY-SCE-Data.xlsx', 'Interest rate expectations', 'Mean probability of higher average interest rate on savings accounts one year from now', 'survey_data/sca-tableall-on-2022-Jul-02.xls', 'ratex_u_all', None, None, None, None, None, None, None, None, None, None, False, 'Interest Rate', 'PROBABILITY OF HIGHER INTEREST RATE NEXT YEAR')
Survey(None, None, None, None, None, 'survey_data/Individual_TBILL.xlsx', 'TBILL6', 'survey_data/medians.xlsx', 'TBILL', 'TBILL_1Y', None, None, None, 'survey_data/table1.xlsx', 'FederalFundsRate_t0', True, 'Nominal Interest Rate', 'EXPECTED NOMINAL INTEREST RATE ONE YEAR AHEAD')