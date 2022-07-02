import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import copy

class Survey:

    def __init__(self, SCE_relative_file_path, SCE_spreadsheet, SCE_column, UMSC_relative_file_path, UMSC_column, variable, y_label):

        SCE_excel = pd.ExcelFile(SCE_relative_file_path)
        SCE_df = pd.read_excel(SCE_excel, SCE_spreadsheet, skiprows=[0, 1, 2])
        SCE_year_month_list = SCE_df.iloc[:, [0]].values.tolist()
        statistic_list = SCE_df.loc[:, SCE_column].tolist()

        for i in range(len(SCE_year_month_list)):
            SCE_year_month_list[i] = str(SCE_year_month_list[i][0])[:4] + '-' + str(SCE_year_month_list[i][0])[4:]

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
                if str(int(year)) + '-' + month not in UMSC_year_month_to_statistic:
                    UMSC_year_month_to_statistic[str(int(year)) + '-' + month] = UMSC_year_to_month_to_statistic[year][temp_month]

        for year_month, statistic in copy.deepcopy(UMSC_year_month_to_statistic).items():
            if statistic == None:
                del UMSC_year_month_to_statistic[year_month]

        UMSC_year_month_list = []
        UMSC_statistic_list = []
        for year_month, statistic in UMSC_year_month_to_statistic.items():
            UMSC_year_month_list.append(year_month)
            UMSC_statistic_list.append(statistic)

        plt.rcParams["figure.figsize"] = [12, 6]
        plt.rcParams["figure.autolayout"] = True
        plt.gcf().canvas.manager.set_window_title('Survey')
        plt.plot(UMSC_year_month_list, UMSC_statistic_list, color = 'red', linewidth = 2, label = 'University of Michigan Survey of Consumers')
        plt.plot(SCE_year_month_list, statistic_list, color = 'blue', linewidth = 2, label = 'Survey of Consumer Expectations')
        plt.title(variable + ' Survey Data', fontweight = 'bold', backgroundcolor = 'silver')
        plt.xlabel('YEAR_MONTH', labelpad = 10)
        plt.ylabel(y_label, labelpad = 10)
        plt.xticks(UMSC_year_month_list[::8], rotation = 45)
        plt.legend(loc = 'upper right')
        plt.grid()

        plt.show()

# inflation
Survey('survey_data/FRBNY-SCE-Data.xlsx', 'Inflation expectations', 'Median one-year ahead expected inflation rate', 'survey_data/sca-tableall-on-2022-Jul-02.xls', 'px1_med_all', 'Inflation', 'EXPECTED INFLATION RATE')
# RGDP
Survey('survey_data/FRBNY-SCE-Data.xlsx', 'Earnings growth', 'Median expected earnings growth', 'survey_data/sca-tableall-on-2022-Jul-02.xls', 'inex_med_all', 'RGDP', 'EXPECTED RGDP GROWTH RATE')
# unemployment
Survey('survey_data/FRBNY-SCE-Data.xlsx', 'Unemployment Expectations', 'Mean probability that the U.S. unemployment rate will be higher one year from now', 'survey_data/sca-tableall-on-2022-Jul-02.xls', 'umex_u_all', 'Unemployment Rate', 'PROBABILITY US UNEMPLOYMENT RATE WILL BE HIGHER NEXT YEAR')
# interest rate
Survey('survey_data/FRBNY-SCE-Data.xlsx', 'Interest rate expectations', 'Mean probability of higher average interest rate on savings accounts one year from now', 'survey_data/sca-tableall-on-2022-Jul-02.xls', 'ratex_u_all', 'Interest Rate', 'PROBABILITY OF HIGHER INTEREST RATE NEXT YEAR')

# https://data.sca.isr.umich.edu/subset/codebook.php
# for UMSC: instead of doing probability, I did the number of people who said it'll go higher