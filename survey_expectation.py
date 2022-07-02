import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import copy

class Survey:

    def __init__(self, SCE_relative_file_path, SCE_spreadsheet, SCE_column, UMSC_relative_file_path, UMSC_column, SPF_relative_file_path, SPF_column, variable, y_label):

        plt.rcParams["figure.figsize"] = [12, 6]
        plt.rcParams["figure.autolayout"] = True
        plt.gcf().canvas.manager.set_window_title('Survey')

        if SPF_relative_file_path is not None:
            self.SPF(SPF_relative_file_path, SPF_column)
        if UMSC_relative_file_path is not None: 
            self.UMSC(UMSC_relative_file_path, UMSC_column)
        if SCE_relative_file_path is not None: 
            self.SCE(SCE_relative_file_path, SCE_spreadsheet, SCE_column)
    
        plt.title(variable + ' Survey Data', fontweight = 'bold', backgroundcolor = 'silver')
        plt.xlabel('YEAR_MONTH', labelpad = 10)
        plt.ylabel(y_label, labelpad = 10)
        # TODO: change
        if SPF_relative_file_path is not None:
            plt.xticks(self.SPF_year_month_list[::8], rotation = 45)
        else:
            plt.xticks(self.UMSC_year_month_list[::8], rotation = 45)
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
    
        plt.plot(self.SCE_year_month_list, self.SCE_statistic_list, color = 'green', linewidth = 2, label = 'Survey of Consumer Expectations')

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

        plt.plot(self.UMSC_year_month_list, self.UMSC_statistic_list, color = 'blue', linewidth = 2, label = 'University of Michigan Survey of Consumers')

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

        plt.plot(self.SPF_year_month_list, self.SPF_statistic_list, color = 'red', linewidth = 2, label = 'Survey of Professional Forecasters')

# inflation
Survey('survey_data/FRBNY-SCE-Data.xlsx', 'Inflation expectations', 'Median one-year ahead expected inflation rate', 'survey_data/sca-tableall-on-2022-Jul-02.xls', 'px1_med_all', 'spf_plot_data/Individual_CPI.xlsx', 'CPI3', 'Inflation', 'EXPECTED INFLATION RATE ONE QUARTER AHEAD')
# RGDP
Survey('survey_data/FRBNY-SCE-Data.xlsx', 'Earnings growth', 'Median expected earnings growth', 'survey_data/sca-tableall-on-2022-Jul-02.xls', 'inex_med_all', None, None, 'RGDP', 'EXPECTED EARNING/INCOME GROWTH RATE ONE QUARTER AHEAD')
Survey(None, None, None, None, None, 'spf_plot_data/Individual_RGDP.xlsx', 'RGDP3', 'RGDP', 'EXPECTED RGDP ONE QUARTER AHEAD')
# unemployment
Survey('survey_data/FRBNY-SCE-Data.xlsx', 'Unemployment Expectations', 'Mean probability that the U.S. unemployment rate will be higher one year from now', 'survey_data/sca-tableall-on-2022-Jul-02.xls', 'umex_u_all', 'survey_data/Individual_PRUNEMP.xlsx', 'PRUNEMP3', 'Unemployment Rate', 'PROBABILITY US UNEMPLOYMENT RATE WILL BE HIGHER NEXT YEAR') # TODO: is this right?
# interest rate
Survey('survey_data/FRBNY-SCE-Data.xlsx', 'Interest rate expectations', 'Mean probability of higher average interest rate on savings accounts one year from now', 'survey_data/sca-tableall-on-2022-Jul-02.xls', 'ratex_u_all', None, None, 'Interest Rate', 'PROBABILITY OF HIGHER INTEREST RATE NEXT YEAR')

# https://data.sca.isr.umich.edu/subset/codebook.php
# for UMSC: instead of doing probability, I did the number of people who said it'll go higher